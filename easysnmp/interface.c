#include <Python.h>

#if PY_VERSION_HEX < 0x02050000
typedef int Py_ssize_t;
#define PY_SSIZE_T_MAX (INT_MAX)
#define PY_SSIZE_T_MIN (INT_MIN)
#endif

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>
#include <net-snmp/snmpv3_api.h>
#include <sys/types.h>
#include <arpa/inet.h>
#include <errno.h>
#include <stdio.h>
#include <fcntl.h>
#include <ctype.h>
#ifdef I_SYS_TIME
#include <sys/time.h>
#endif
#include <netdb.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>

#ifdef HAVE_REGEX_H
#include <regex.h>
#endif

#define STRLEN(x) ((x) ? strlen((x)) : 0)

#define SUCCESS (1)
#define FAILURE (0)

#define VARBIND_TAG_F  (0)
#define VARBIND_IID_F  (1)
#define VARBIND_VAL_F  (2)
#define VARBIND_TYPE_F (3)

#define TYPE_UNKNOWN      (0)
#define MAX_TYPE_NAME_LEN (32)
#define STR_BUF_SIZE      ((MAX_TYPE_NAME_LEN) * (MAX_OID_LEN))
#define ENG_ID_BUF_SIZE   (32)

#define NO_RETRY_NOSUCH (0)

#define USE_NUMERIC_OIDS (0x08)
#define NON_LEAF_NAME    (0x04)
#define USE_LONG_NAMES   (0x02)
#define FAIL_ON_NULL_IID (0x01)
#define NO_FLAGS         (0x00)

#define SAFE_FREE(x)                                                          \
    do                                                                        \
    {                                                                         \
        if (x != NULL)                                                        \
        {                                                                     \
            free(x);                                                          \
        }                                                                     \
    }                                                                         \
    while (0)

typedef netsnmp_session SnmpSession;
typedef struct tree SnmpMibNode;
static int __is_numeric_oid(char *oidstr);
static int __is_leaf(struct tree *tp);
static int __translate_appl_type(char *typestr);
static int __translate_asn_type(int type);
static int __snprint_value(char *buf, size_t buf_len,
                           netsnmp_variable_list *var,
                           struct tree *tp, int type, int flag);
static int __sprint_num_objid(char *buf, oid *objid, int len);
static int __scan_num_objid(char *buf, oid *objid, size_t *len);
static int __get_type_str(int type, char *str, int log_error);
static int __get_label_iid(char *name, char **last_label, char **iid,
                           int flag);
static struct tree *__tag2oid(char *tag, char *iid, oid *oid_arr,
                              int *oid_arr_len, int *type, int best_guess);
static int __concat_oid_str(oid *doid_arr, int *doid_arr_len, char *soid_str);
static int __add_var_val_str(netsnmp_pdu *pdu, oid *name, int name_length,
                             char *val, int len, int type);

static void py_log_msg(int log_level, char *printf_fmt, ...);

enum { INFO, WARNING, ERROR, DEBUG, EXCEPTION };

static PyObject *easysnmp_import = NULL;
static PyObject *easysnmp_exceptions_import = NULL;
static PyObject *easysnmp_compat_import = NULL;
static PyObject *logging_import = NULL;

static PyObject *PyLogger = NULL;
static PyObject *EasySNMPError = NULL;
static PyObject *EasySNMPConnectionError = NULL;
static PyObject *EasySNMPTimeoutError = NULL;
static PyObject *EasySNMPUnknownObjectIDError = NULL;
static PyObject *EasySNMPNoSuchObjectError = NULL;
static PyObject *EasySNMPUndeterminedTypeError = NULL;

/*
 * Ripped wholesale from library/tools.h from Net-SNMP 5.7.3
 * to remain compatible with versions 5.7.2 and earlier.
 */
static void *compat_netsnmp_memdup(const void *from, size_t size)
{
    void *to = NULL;

    if (from)
    {
        to = malloc(size);
        if (to)
        {
            memcpy(to, from, size);
        }
    }
    return to;
}

void __libraries_init(char *appname)
{
    static int have_inited = 0;

    if (have_inited)
    {
        return;
    }
    have_inited = 1;

    snmp_set_quick_print(1);
    snmp_enable_stderrlog();
    init_snmp(appname);

    netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID,
                           NETSNMP_DS_LIB_DONT_BREAKDOWN_OIDS, 1);
    netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID,
                       NETSNMP_DS_LIB_PRINT_SUFFIX_ONLY, 1);
    netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_OID_OUTPUT_FORMAT,
                       NETSNMP_OID_OUTPUT_SUFFIX);
}

static int __is_numeric_oid(char *oidstr)
{
    if (!oidstr)
    {
        return 0;
    }
    for (; *oidstr; oidstr++)
    {
        if (isalpha((int)*oidstr))
        {
            return 0;
        }
    }
    return 1;
}

static int __is_leaf(struct tree *tp)
{
    char buf[MAX_TYPE_NAME_LEN];
    return (tp && (__get_type_str(tp->type, buf, 0) ||
                   (tp->parent && __get_type_str(tp->parent->type, buf, 0))));
}

static int __translate_appl_type(char *typestr)
{
    if (typestr == NULL || *typestr == '\0')
    {
        return TYPE_UNKNOWN;
    }

    if (!strncasecmp(typestr, "INTEGER32", 8))
    {
        return TYPE_INTEGER32;
    }
    if (!strncasecmp(typestr, "INTEGER", 3))
    {
        return TYPE_INTEGER;
    }
    if (!strncasecmp(typestr, "UNSIGNED32", 3))
    {
        return TYPE_UNSIGNED32;
    }
    if (!strcasecmp(typestr, "COUNTER")) /* check all in case counter64 */
    {
        return TYPE_COUNTER;
    }
    if (!strncasecmp(typestr, "GAUGE", 3))
    {
        return TYPE_GAUGE;
    }
    if (!strncasecmp(typestr, "IPADDR", 3))
    {
        return TYPE_IPADDR;
    }
    if (!strncasecmp(typestr, "OCTETSTR", 3))
    {
        return TYPE_OCTETSTR;
    }
    if (!strncasecmp(typestr, "TICKS", 3))
    {
        return TYPE_TIMETICKS;
    }
    if (!strncasecmp(typestr, "OPAQUE", 3))
    {
        return TYPE_OPAQUE;
    }
    if (!strncasecmp(typestr, "OBJECTID", 3))
    {
        return TYPE_OBJID;
    }
    if (!strncasecmp(typestr, "NETADDR", 3))
    {
        return TYPE_NETADDR;
    }
    if (!strncasecmp(typestr, "COUNTER64", 3))
    {
        return TYPE_COUNTER64;
    }
    if (!strncasecmp(typestr, "NULL", 3))
    {
        return TYPE_NULL;
    }
    if (!strncasecmp(typestr, "BITS", 3))
    {
        return TYPE_BITSTRING;
    }
    if (!strncasecmp(typestr, "ENDOFMIBVIEW", 3))
    {
        return SNMP_ENDOFMIBVIEW;
    }
    if (!strncasecmp(typestr, "NOSUCHOBJECT", 7))
    {
        return SNMP_NOSUCHOBJECT;
    }
    if (!strncasecmp(typestr, "NOSUCHINSTANCE", 7))
    {
        return SNMP_NOSUCHINSTANCE;
    }
    if (!strncasecmp(typestr, "UINTEGER", 3))
    {
        return (TYPE_UINTEGER); /* historic - should not show up */
                                /* but it does?                  */
    }
    if (!strncasecmp(typestr, "NOTIF", 3))
    {
        return TYPE_NOTIFTYPE;
    }
    if (!strncasecmp(typestr, "TRAP", 4))
    {
        return TYPE_TRAPTYPE;
    }
    return TYPE_UNKNOWN;
}

static int __translate_asn_type(int type)
{
    switch (type)
    {
        case ASN_INTEGER:
            return TYPE_INTEGER;
        case ASN_OCTET_STR:
            return TYPE_OCTETSTR;
        case ASN_OPAQUE:
            return TYPE_OPAQUE;
        case ASN_OBJECT_ID:
            return TYPE_OBJID;
        case ASN_TIMETICKS:
            return TYPE_TIMETICKS;
        case ASN_GAUGE:
            return TYPE_GAUGE;
        case ASN_COUNTER:
            return TYPE_COUNTER;
        case ASN_IPADDRESS:
            return TYPE_IPADDR;
        case ASN_BIT_STR:
            return TYPE_BITSTRING;
        case ASN_NULL:
            return TYPE_NULL;
        /* no translation for these exception type values */
        case SNMP_ENDOFMIBVIEW:
        case SNMP_NOSUCHOBJECT:
        case SNMP_NOSUCHINSTANCE:
            return type;
        case ASN_UINTEGER:
            return TYPE_UINTEGER;
        case ASN_COUNTER64:
            return TYPE_COUNTER64;
        default:
            py_log_msg(ERROR, "translate_asn_type: unhandled asn type (%d)",
                       type);

            return TYPE_OTHER;
    }
}

#define USE_BASIC        (0)
#define USE_ENUMS        (1)
#define USE_SPRINT_VALUE (2)
static int __snprint_value(char *buf, size_t buf_len,
                           netsnmp_variable_list *var,
                           struct tree *tp, int type, int flag)
{
    int len = 0;
    u_char *ip;
    struct enum_list *ep;

    buf[0] = '\0';
    if (flag == USE_SPRINT_VALUE)
    {
        snprint_value(buf, buf_len, var->name, var->name_length, var);
        len = STRLEN(buf);
    }
    else
    {
        switch (var->type)
        {
            case ASN_INTEGER:
                if (flag == USE_ENUMS)
                {
                   for (ep = tp->enums; ep; ep = ep->next)
                   {
                       if (ep->value == *var->val.integer)
                       {
                           strlcpy(buf, ep->label, buf_len);
                           len = STRLEN(buf);
                           break;
                       }
                   }
                }
                if (!len)
                {
                    snprintf(buf, buf_len, "%ld", *var->val.integer);
                    len = STRLEN(buf);
                }
                break;

            case ASN_GAUGE:
            case ASN_COUNTER:
            case ASN_TIMETICKS:
            case ASN_UINTEGER:
                snprintf(buf, buf_len, "%lu",
                         (unsigned long) *var->val.integer);
                len = STRLEN(buf);
                break;

            case ASN_OCTET_STR:
            case ASN_OPAQUE:
                len = var->val_len;
                if (len > buf_len)
                {
                    len = buf_len;
                }
                memcpy(buf, (char *)var->val.string, len);
                break;

            case ASN_IPADDRESS:
                ip = (u_char *)var->val.string;
                snprintf(buf, buf_len, "%d.%d.%d.%d", ip[0], ip[1],
                         ip[2], ip[3]);
                len = STRLEN(buf);
                break;

            case ASN_NULL:
                break;

            case ASN_OBJECT_ID:
                __sprint_num_objid(buf, (oid *)(var->val.objid),
                                   var->val_len/sizeof(oid));
                len = STRLEN(buf);
                break;

            case SNMP_ENDOFMIBVIEW:
                snprintf(buf, buf_len, "%s", "ENDOFMIBVIEW");
                len = STRLEN(buf);
                break;
            case SNMP_NOSUCHOBJECT:
                snprintf(buf, buf_len, "%s", "NOSUCHOBJECT");
                len = STRLEN(buf);
                break;
            case SNMP_NOSUCHINSTANCE:
                snprintf(buf, buf_len, "%s", "NOSUCHINSTANCE");
                len = STRLEN(buf);
                break;

            case ASN_COUNTER64:
#ifdef OPAQUE_SPECIAL_TYPES
            case ASN_OPAQUE_COUNTER64:
            case ASN_OPAQUE_U64:
#endif
                printU64(buf, (struct counter64 *)var->val.counter64);
                len = STRLEN(buf);
                break;

#ifdef OPAQUE_SPECIAL_TYPES
            case ASN_OPAQUE_I64:
                printI64(buf, (struct counter64 *)var->val.counter64);
                len = STRLEN(buf);
                break;
#endif

            case ASN_BIT_STR:
                snprint_bitstring(buf, buf_len, var, NULL, NULL, NULL);
                len = STRLEN(buf);
                break;
#ifdef OPAQUE_SPECIAL_TYPES
            case ASN_OPAQUE_FLOAT:
                if (var->val.floatVal)
                {
                    snprintf(buf, buf_len, "%f", *var->val.floatVal);
                }
                break;

            case ASN_OPAQUE_DOUBLE:
                if (var->val.doubleVal)
                {
                    snprintf(buf, buf_len, "%f", *var->val.doubleVal);
                }
                break;
#endif

            case ASN_NSAP:
            default:
                py_log_msg(ERROR, "snprint_value: asn type not handled %d",
                           var->type);
        }
    }
    return len;
}

static int __sprint_num_objid(char *buf, oid *objid, int len)
{
    int i;
    buf[0] = '\0';
    for (i = 0; i < len; i++)
    {
        sprintf(buf, ".%lu", *objid++);
        buf += STRLEN(buf);
    }
    return SUCCESS;
}

static int __scan_num_objid(char *buf, oid *objid, size_t *len)
{
    char *cp;
    *len = 0;
    if (*buf == '.')
    {
        buf++;
    }
    cp = buf;
    while (*buf)
    {
        if (*buf++ == '.')
        {
            sscanf(cp, "%lu", objid++);
            /* *objid++ = atoi(cp); */
            (*len)++;
            cp = buf;
        }
        else
        {
            if (isalpha((int)*buf))
            {
                return FAILURE;
            }
        }
    }
    sscanf(cp, "%lu", objid++);
    /* *objid++ = atoi(cp); */
    (*len)++;
    return SUCCESS;
}

static int __get_type_str(int type, char *str, int log_error)
{
    switch (type)
    {
        case TYPE_OBJID:
            strcpy(str, "OBJECTID");
            break;
        case TYPE_OCTETSTR:
            strcpy(str, "OCTETSTR");
            break;
        case TYPE_INTEGER:
            strcpy(str, "INTEGER");
            break;
        case TYPE_INTEGER32:
            strcpy(str, "INTEGER32");
            break;
        case TYPE_UNSIGNED32:
            strcpy(str, "UNSIGNED32");
            break;
        case TYPE_NETADDR:
            strcpy(str, "NETADDR");
            break;
        case TYPE_IPADDR:
            strcpy(str, "IPADDR");
            break;
        case TYPE_COUNTER:
            strcpy(str, "COUNTER");
            break;
        case TYPE_GAUGE:
            strcpy(str, "GAUGE");
            break;
        case TYPE_TIMETICKS:
            strcpy(str, "TICKS");
            break;
        case TYPE_OPAQUE:
            strcpy(str, "OPAQUE");
            break;
        case TYPE_COUNTER64:
            strcpy(str, "COUNTER64");
            break;
        case TYPE_NULL:
            strcpy(str, "NULL");
            break;
        case SNMP_ENDOFMIBVIEW:
            strcpy(str, "ENDOFMIBVIEW");
            break;
        case SNMP_NOSUCHOBJECT:
            strcpy(str, "NOSUCHOBJECT");
            break;
        case SNMP_NOSUCHINSTANCE:
            strcpy(str, "NOSUCHINSTANCE");
            break;
        case TYPE_UINTEGER:
            strcpy(str, "UINTEGER"); /* historic - should not show up */
                                     /* but it does?                  */
            break;
        case TYPE_NOTIFTYPE:
            strcpy(str, "NOTIF");
            break;
        case TYPE_BITSTRING:
            strcpy(str, "BITS");
            break;
        case TYPE_TRAPTYPE:
            strcpy(str, "TRAP");
            break;
        case TYPE_OTHER: /* not sure if this is a valid leaf type?? */
        case TYPE_NSAPADDRESS:
        default: /* unsupported types for now */
            strcpy(str, "");
            if (log_error)
            {
                py_log_msg(ERROR, "unspported type found: %d", type);
            }
            return FAILURE;
    }
    return SUCCESS;
}

/* does a destructive disection of <label1>...<labeln>.<iid> returning
   <labeln> and <iid> in seperate strings (note: will destructively
   alter input string, 'name') */
static int __get_label_iid(char *name, char **last_label, char **iid,
                           int flag)
{
    char *lcp;
    char *icp;
    int len = STRLEN(name);
    int found_label = 0;

    *last_label = *iid = NULL;

    if (len == 0)
    {
        return FAILURE;
    }

    /* Handle case where numeric oid's have been requested.  The input 'name'
    ** in this case should be a numeric OID -- return failure if not.
    */
    if ((flag & USE_NUMERIC_OIDS))
    {
        if (!__is_numeric_oid(name))
        {
            return FAILURE ;
        }

        /* Walk backward through the string, looking for first two '.' chars */
        lcp = &(name[len]);
        icp = NULL;
        while (lcp > name)
        {
            if (*lcp == '.')
            {
                /* If this is the first occurence of '.', note it in icp.
                ** Otherwise, this must be the second occurrence, so break
                ** out of the loop.
                */
                if (icp == NULL)
                {
                    icp = lcp;
                }
                else
                {
                    break;
                }
            }
            lcp--;
        }

        /* Make sure we found at least a label and index. */
        if (!icp)
        {
            return FAILURE;
        }

        /* Push forward past leading '.' chars and separate the strings. */
        lcp++;
        *icp++ = '\0';

        *last_label = (flag & USE_LONG_NAMES) ? name : lcp;
        *iid        = icp;

        return SUCCESS;
    }

    lcp = icp = &(name[len]);

    while (lcp > name)
    {
        if (*lcp == '.')
        {
            if (found_label)
            {
                lcp++;
                break;
            }
            else
            {
                icp = lcp;
            }
        }
        if (!found_label && isalpha((int)*lcp))
        {
            found_label = 1;
        }
        lcp--;
    }

    if (!found_label ||
        (!isdigit((int)*(icp + 1)) && (flag & FAIL_ON_NULL_IID)))
    {
        return FAILURE;
    }

    if (flag & NON_LEAF_NAME) /* dont know where to start instance id */
    {
        /* put the whole thing in label */
        icp = &(name[len]);
        flag |= USE_LONG_NAMES;
        /* special hack in case no mib loaded - object identifiers will
         * start with .iso.<num>.<num>...., in which case it is preferable
         * to make the label entirely numeric (i.e., convert "iso" => "1")
         */
        if (*lcp == '.' && lcp == name)
        {
            if (!strncmp(".ccitt.", lcp, 7))
            {
                name += 2;
                *name = '.';
                *(name + 1) = '0';
            }
            else if (!strncmp(".iso.", lcp, 5))
            {
                name += 2;
                *name = '.';
                *(name + 1) = '1';
            }
            else if (!strncmp(".joint-iso-ccitt.", lcp, 17))
            {
                name += 2;
                *name = '.';
                *(name + 1) = '2';
            }
        }
    }
    else if (*icp)
    {
        *(icp++) = '\0';
    }
    *last_label = (flag & USE_LONG_NAMES ? name : lcp);

    *iid = icp;

    return SUCCESS;
}

/* Convert a tag (string) to an OID array              */
/* Tag can be either a symbolic name, or an OID string */
static struct tree *__tag2oid(char *tag, char *iid, oid *oid_arr,
                              int *oid_arr_len, int *type, int best_guess)
{
    struct tree *tp = NULL;
    struct tree *rtp = NULL;
    oid newname[MAX_OID_LEN], *op;
    size_t newname_len = 0;

    if (type)
    {
        *type = TYPE_UNKNOWN;
    }
    if (oid_arr_len)
    {
        *oid_arr_len = 0;
    }
    if (!tag)
    {
        goto done;
    }

    /*********************************************************/
    /* best_guess = 0 - same as no switches (read_objid)     */
    /*                  if multiple parts, or uses find_node */
    /*                  if a single leaf                     */
    /* best_guess = 1 - same as -Ib (get_wild_node)          */
    /* best_guess = 2 - same as -IR (get_node)               */
    /*********************************************************/

    /* numeric scalar                (1,2) */
    /* single symbolic               (1,2) */
    /* single regex                  (1)   */
    /* partial full symbolic         (2)   */
    /* full symbolic                 (2)   */
    /* module::single symbolic       (2)   */
    /* module::partial full symbolic (2)   */
    if (best_guess == 1 || best_guess == 2)
    {
        /* make sure it's not a numeric tag */
        if (!__scan_num_objid(tag, newname, &newname_len))
        {
            newname_len = MAX_OID_LEN;
            if (best_guess == 2) /* Random search -IR */
            {
                if (get_node(tag, newname, &newname_len))
                {
                    rtp = tp = get_tree(newname, newname_len, get_tree_head());
                }
            }
            else if (best_guess == 1) /* Regex search -Ib */
            {
                clear_tree_flags(get_tree_head());
                if (get_wild_node(tag, newname, &newname_len))
                {
                    rtp = tp = get_tree(newname, newname_len, get_tree_head());
                }
            }
        }
        else
        {
            rtp = tp = get_tree(newname, newname_len, get_tree_head());
        }
        if (type)
        {
            *type = (tp ? tp->type : TYPE_UNKNOWN);
        }
        if ((oid_arr == NULL) || (oid_arr_len == NULL))
        {
            return rtp;
        }
        memcpy(oid_arr, (char *)newname, newname_len*sizeof(oid));
        *oid_arr_len = newname_len;
    }
    /* if best_guess is off and multi part tag or module::tag */
    /* numeric scalar                                         */
    /* module::single symbolic                                */
    /* module::partial full symbolic                          */
    /* FULL symbolic OID                                      */
    else if (strchr(tag, '.') || strchr(tag, ':'))
    {
        /* make sure it's not a numeric tag */
        if (!__scan_num_objid(tag, newname, &newname_len))
        {
            newname_len = MAX_OID_LEN;
            if (read_objid(tag, newname, &newname_len)) /* long name */
            {
                rtp = tp = get_tree(newname, newname_len, get_tree_head());
            }
            else
            {
                /* failed to parse the OID */
                newname_len = 0;
            }
        }
        else
        {
            rtp = tp = get_tree(newname, newname_len, get_tree_head());
        }
        if (type)
        {
            *type = (tp ? tp->type : TYPE_UNKNOWN);
        }
        if ((oid_arr == NULL) || (oid_arr_len == NULL))
        {
            return rtp;
        }
        memcpy(oid_arr, (char *)newname, newname_len*sizeof(oid));
        *oid_arr_len = newname_len;
    }
    /* else best_guess is off and it is a single leaf */
    /* single symbolic                                */
    else
    {
        rtp = tp = find_node(tag, get_tree_head());
        if (tp)
        {
            if (type)
            {
                *type = tp->type;
            }
            if ((oid_arr == NULL) || (oid_arr_len == NULL))
            {
                return rtp;
            }
            /* code taken from get_node in snmp_client.c */
            for (op = newname + MAX_OID_LEN - 1; op >= newname; op--)
            {
                *op = tp->subid;
                tp = tp->parent;
                if (tp == NULL)
                {
                    break;
                }
            }
            *oid_arr_len = newname + MAX_OID_LEN - op;
            memcpy(oid_arr, op, *oid_arr_len * sizeof(oid));
        }
        else
        {
            return rtp; /* HACK: otherwise, concat_oid_str confuses things */
        }
    }

done:

    if (iid && *iid && oid_arr_len)
    {
        __concat_oid_str(oid_arr, oid_arr_len, iid);
    }
    return rtp;
}

/* function: __concat_oid_str
 *
 * This function converts a dotted-decimal string, soid_str, to an array
 * of oid types and concatenates them on doid_arr begining at the index
 * specified by doid_arr_len.
 *
 * returns : SUCCESS, FAILURE
 */
static int __concat_oid_str(oid *doid_arr, int *doid_arr_len, char *soid_str)
{
    char *soid_buf;
    char *cp;
    char *st;

    if (!soid_str || !*soid_str)
    {
        return SUCCESS; /* successfully added nothing */
    }
    if (*soid_str == '.')
    {
        soid_str++;
    }
    soid_buf = strdup(soid_str);
    if (!soid_buf)
    {
        return FAILURE;
    }
    cp = strtok_r(soid_buf, ".", &st);
    while (cp)
    {
        sscanf(cp, "%lu", &(doid_arr[(*doid_arr_len)++]));
        /* doid_arr[(*doid_arr_len)++] = atoi(cp); */
        cp = strtok_r(NULL, ".", &st);
    }
    free(soid_buf);
    return SUCCESS;
}

/* add a varbind to PDU */
static int __add_var_val_str(netsnmp_pdu *pdu, oid *name, int name_length,
                             char *val, int len, int type)
{
    netsnmp_variable_list *vars;
    oid oidbuf[MAX_OID_LEN];
    int ret = SUCCESS;

    if (pdu->variables == NULL)
    {
        vars = (netsnmp_variable_list *) calloc(1, sizeof(netsnmp_variable_list));
        pdu->variables = vars;
    }
    else
    {
        /* make a copy of PDU variables */
        for (vars = pdu->variables;
             vars->next_variable;
             vars = vars->next_variable)
        {
            /* EXIT */;
        }

        vars->next_variable =
            (netsnmp_variable_list *) calloc(1, sizeof(netsnmp_variable_list));
        vars = vars->next_variable;
    }

    vars->next_variable = NULL;
    vars->name = snmp_duplicate_objid(name, name_length);
    vars->name_length = name_length;
    switch (type)
    {
        case TYPE_INTEGER:
        case TYPE_INTEGER32:
            vars->type = ASN_INTEGER;
            vars->val.integer = malloc(sizeof(long));
            if (val)
            {
                *(vars->val.integer) = strtol(val, NULL, 0);
            }
            else
            {
                ret = FAILURE;
                *(vars->val.integer) = 0;
            }
            vars->val_len = sizeof(long);
            break;

        case TYPE_GAUGE:
        case TYPE_UNSIGNED32:
            vars->type = ASN_GAUGE;
            goto UINT;
        case TYPE_COUNTER:
            vars->type = ASN_COUNTER;
            goto UINT;
        case TYPE_TIMETICKS:
            vars->type = ASN_TIMETICKS;
            goto UINT;
        case TYPE_UINTEGER:
            vars->type = ASN_UINTEGER;

UINT:

            vars->val.integer = malloc(sizeof(long));
            if (val)
            {
                sscanf(val, "%lu", vars->val.integer);
            }
            else
            {
                ret = FAILURE;
                *(vars->val.integer) = 0;
            }
            vars->val_len = sizeof(long);
            break;

        case TYPE_OCTETSTR:
            vars->type = ASN_OCTET_STR;
            goto OCT;

        case TYPE_BITSTRING:
            vars->type = ASN_OCTET_STR;
            goto OCT;

        case TYPE_OPAQUE:
            vars->type = ASN_OCTET_STR;

OCT:

            vars->val.string = malloc(len);
            vars->val_len = len;
            if (val && len)
            {
                memcpy((char *)vars->val.string, val, len);
            }
            else
            {
                ret = FAILURE;
                vars->val.string = (u_char *)strdup("");
                vars->val_len = 0;
            }
            break;

        case TYPE_IPADDR:
            vars->type = ASN_IPADDRESS;
            {
                in_addr_t addr;

                if (val)
                {
                    addr = inet_addr(val);
                }
                else
                {
                    ret = FAILURE;
                    addr = 0;
                }
                vars->val.integer = compat_netsnmp_memdup(&addr, sizeof(addr));
                vars->val_len = sizeof(addr);
            }
            break;

        case TYPE_OBJID:
            vars->type = ASN_OBJECT_ID;
            vars->val_len = MAX_OID_LEN;
            /* if (read_objid(val, oidbuf, &(vars->val_len))) { */
            /* tp = __tag2oid(val, NULL, oidbuf, &(vars->val_len), NULL, 0); */
            if (!val || !snmp_parse_oid(val, oidbuf, &vars->val_len))
            {
                vars->val.objid = NULL;
                ret = FAILURE;
            }
            else
            {
                vars->val.objid = snmp_duplicate_objid(oidbuf, vars->val_len);
                vars->val_len *= sizeof(oid);
            }
            break;

        default:
            vars->type = ASN_NULL;
            vars->val_len = 0;
            vars->val.string = NULL;
            ret = FAILURE;
    }

    return ret;
}

/* takes ss and pdu as input and updates the 'response' argument */
/* the input 'pdu' argument will be freed */
static int __send_sync_pdu(netsnmp_session *ss, netsnmp_pdu *pdu,
                           netsnmp_pdu **response, int retry_nosuch,
                           char *err_str, int *err_num, int *err_ind)
{
    int status = 0;
    long command = pdu->command;
    char *tmp_err_str;

    *err_num = 0;
    *err_ind = 0;
    *response = NULL;
    tmp_err_str = NULL;
    memset(err_str, '\0', STR_BUF_SIZE);

    if (ss == NULL)
    {
        *err_num = 0;
        *err_ind = SNMPERR_BAD_SESSION;
        status = SNMPERR_BAD_SESSION;
        strlcpy(err_str, snmp_api_errstring(*err_ind), STR_BUF_SIZE);
        goto done;
    }

retry:

    Py_BEGIN_ALLOW_THREADS
    status = snmp_sess_synch_response(ss, pdu, response);
    Py_END_ALLOW_THREADS

    if ((*response == NULL) && (status == STAT_SUCCESS))
    {
        status = STAT_ERROR;
    }

    // SNMP v3 doesn't quite raise timeouts correctly, so we correct it
    if (strcmp(err_str, "Timeout") && (status == STAT_ERROR))
    {
        status = STAT_TIMEOUT;
    }

    switch (status)
    {
        case STAT_SUCCESS:
            status = (*response)->errstat;
            switch (status)
            {
                case SNMP_ERR_NOERROR:
                    break;

                case SNMP_ERR_NOSUCHNAME:
                    if (retry_nosuch &&
                        (pdu = snmp_fix_pdu(*response, command)))
                    {
                        if (*response)
                        {
                            snmp_free_pdu(*response);
                        }
                        goto retry;
                    }
                    PyErr_SetString(EasySNMPNoSuchObjectError,
                                    "no such object could be found");
                    break;

                /* Pv1, SNMPsec, Pv2p, v2c, v2u, v2*, and SNMPv3 PDUs */
                case SNMP_ERR_TOOBIG:
                case SNMP_ERR_BADVALUE:
                case SNMP_ERR_READONLY:
                case SNMP_ERR_GENERR:
                /* in SNMPv2p, SNMPv2c, SNMPv2u, SNMPv2*, and SNMPv3 PDUs */
                case SNMP_ERR_NOACCESS:
                case SNMP_ERR_WRONGTYPE:
                case SNMP_ERR_WRONGLENGTH:
                case SNMP_ERR_WRONGENCODING:
                case SNMP_ERR_WRONGVALUE:
                case SNMP_ERR_NOCREATION:
                case SNMP_ERR_INCONSISTENTVALUE:
                case SNMP_ERR_RESOURCEUNAVAILABLE:
                case SNMP_ERR_COMMITFAILED:
                case SNMP_ERR_UNDOFAILED:
                case SNMP_ERR_AUTHORIZATIONERROR:
                case SNMP_ERR_NOTWRITABLE:
                /* in SNMPv2c, SNMPv2u, SNMPv2*, and SNMPv3 PDUs */
                case SNMP_ERR_INCONSISTENTNAME:
                default:
                    strlcpy(err_str,
                            (char *)snmp_errstring((*response)->errstat),
                            STR_BUF_SIZE);
                    *err_num = (int)(*response)->errstat;
                    *err_ind = (*response)->errindex;
                    py_log_msg(DEBUG, "sync PDU: %s", err_str);

                    PyErr_SetString(EasySNMPError, err_str);
                    break;
             }
             break;

        case STAT_TIMEOUT:
            snmp_sess_error(ss, err_num, err_ind, &tmp_err_str);
            strlcpy(err_str, tmp_err_str, STR_BUF_SIZE);
            py_log_msg(DEBUG, "sync PDU: %s", err_str);

            PyErr_SetString(EasySNMPTimeoutError,
                            "timed out while connecting to remote host");
            break;

        case STAT_ERROR:
            snmp_sess_error(ss, err_num, err_ind, &tmp_err_str);
            strlcpy(err_str, tmp_err_str, STR_BUF_SIZE);
            py_log_msg(DEBUG, "sync PDU: %s", err_str);

            PyErr_SetString(EasySNMPError, tmp_err_str);
            break;

        default:
            strcat(err_str, "send_sync_pdu: unknown status");
            *err_num = ss->s_snmp_errno;
            py_log_msg(DEBUG, "sync PDU: %s", err_str);

            break;
    }

done:

    if (tmp_err_str)
    {
        free(tmp_err_str);
    }

    return status;
}

static PyObject *py_netsnmp_construct_varbind(void)
{
    return PyObject_CallMethod(easysnmp_import, "SNMPVariable", NULL);
}

static int py_netsnmp_attr_string(PyObject *obj, char *attr_name, char **val,
                                  Py_ssize_t *len)
{
    *val = NULL;
    if (obj && attr_name && PyObject_HasAttrString(obj, attr_name))
    {
        PyObject *attr = PyObject_GetAttrString(obj, attr_name);
        if (attr)
        {
            int retval;

#if PY_MAJOR_VERSION >= 3
            // Encode the provided attribute using latin-1 into bytes and
            // retrieve its value and length
            PyObject *attr_bytes = PyUnicode_AsEncodedString(attr, "latin-1",
                                                             "surrogateescape");
            if (!attr_bytes)
            {
                return -1;
            }
            retval = PyBytes_AsStringAndSize(attr_bytes, val, len);
#else
            retval = PyString_AsStringAndSize(attr, val, len);
#endif

            Py_DECREF(attr);
            return retval;
        }
    }

    return -1;
}

static long long py_netsnmp_attr_long(PyObject *obj, char *attr_name)
{
    long long val = -1;

    if (obj && attr_name && PyObject_HasAttrString(obj, attr_name))
    {
        PyObject *attr = PyObject_GetAttrString(obj, attr_name);
        if (attr)
        {
            val = PyLong_AsLong(attr);
            Py_DECREF(attr);
        }
    }

    return val;
}

static void *py_netsnmp_attr_void_ptr(PyObject *obj, char *attr_name)
{
    void *val = NULL;

    if (obj && attr_name && PyObject_HasAttrString(obj, attr_name))
    {
        PyObject *attr = PyObject_GetAttrString(obj, attr_name);
        if (attr)
        {
            val = PyLong_AsVoidPtr(attr);
            Py_DECREF(attr);
        }
    }

    return val;
}

static int py_netsnmp_attr_set_string(PyObject *obj, char *attr_name,
                                      char *val, size_t len)
{
    int ret = -1;
    if (obj && attr_name)
    {
        PyObject* val_obj = PyUnicode_Decode(val, len, "latin-1",
                                             "surrogateescape");
        if (!val_obj)
        {
            return -1;
        }
        ret = PyObject_SetAttrString(obj, attr_name, val_obj);
        Py_DECREF(val_obj);
    }
    return ret;
}

/**
 * Update python session object error attributes.
 *
 * Copy the error info which may have been returned from __send_sync_pdu(...)
 * into the python object. This will allow the python code to determine if
 * an error occured during an snmp operation.
 *
 * Currently there are 3 attributes we care about
 *
 * error_number - Copy of the value of netsnmp_session.s_errno. This is the
 * system errno that was generated during our last call into the net-snmp
 * library.
 *
 * error_index - Copy of the value of netsmp_session.s_snmp_errno. These error
 * numbers are separate from the system errno's and describe SNMP errors.
 *
 * error_string - A string describing the error_index that was returned during
 * our last operation.
 *
 * @param[in] session The python object that represents our current Session
 * @param[in|out] err_str A string describing err_ind
 * @param[in|out] err_num The system errno currently stored by our session
 * @param[in|out] err_ind The snmp errno currently stored by our session
 */
static void __py_netsnmp_update_session_errors(PyObject *session,
                                               char *err_str, int err_num,
                                               int err_ind)
{
    PyObject *tmp_for_conversion;

    py_netsnmp_attr_set_string(session, "error_string", err_str,
                               STRLEN(err_str));

    tmp_for_conversion = PyLong_FromLong(err_num);
    if (!tmp_for_conversion)
    {
        return; /* nothing better to do? */
    }
    PyObject_SetAttrString(session, "error_number", tmp_for_conversion);
    Py_DECREF(tmp_for_conversion);

    tmp_for_conversion = PyLong_FromLong(err_ind);
    if (!tmp_for_conversion)
    {
        return; /* nothing better to do? */
    }
    PyObject_SetAttrString(session, "error_index", tmp_for_conversion);
    Py_DECREF(tmp_for_conversion);
}

/*
 * We create a custom little wrapper around snmp_sess_open which disables
 * stderr during the call to avoid errors printed to stderr such as:
 *
 * getaddrinfo: <hostname> Name or service not known
 *
 * These errors are already handled by Python exceptions are are not needed.
 */
void *snmp_sess_open_quiet(SnmpSession *session)
{
    int original_stderr;
    int dev_null;
    SnmpSession *ss = NULL;

    // Redirect stderr to /dev/null
    original_stderr = dup(STDERR_FILENO);
    dev_null = open("/dev/null", O_WRONLY);
    dup2(dev_null, STDERR_FILENO);
    close(dev_null);

    // Open the session
    ss = snmp_sess_open(session);

    // Restore stderr output
    dup2(original_stderr, STDERR_FILENO);
    close(original_stderr);

    return ss;
}

static PyObject *netsnmp_create_session(PyObject *self, PyObject *args)
{
    int version;
    char *community;
    char *peer;
    int lport;
    int retries;
    int timeout;
    SnmpSession session = {0};
    SnmpSession *ss = NULL;
    int error = 0;

    if (!PyArg_ParseTuple(args, "issiii", &version, &community, &peer, &lport,
                          &retries, &timeout))
    {
        return NULL;
    }

    __libraries_init("python");

    snmp_sess_init(&session);

    session.version = -1;
#ifndef DISABLE_SNMPV1
    if (version == 1)
    {
        session.version = SNMP_VERSION_1;
    }
#endif
#ifndef DISABLE_SNMPV2C
    if (version == 2)
    {
        session.version = SNMP_VERSION_2c;
    }
#endif
    if (version == 3)
    {
        session.version = SNMP_VERSION_3;
    }
    if (session.version == -1)
    {
        PyErr_Format(PyExc_ValueError, "unsupported SNMP version (%d)",
                     version);
        error = 1;
        goto end;
    }

    session.community_len = STRLEN((char *)community);
    session.community = (u_char *)community;
    session.peername = peer;
    session.local_port = lport;
    session.retries = retries; /* 5 */
    session.timeout = timeout; /* 1000000L */
    session.authenticator = NULL;

    ss = snmp_sess_open_quiet(&session);

    if (ss == NULL)
    {
        PyErr_SetString(EasySNMPConnectionError, "couldn't open SNMP session");
        error = 1;
    }

end:

    if (error)
    {
        return NULL;
    }
    else
    {
        return PyLong_FromVoidPtr((void *)ss);
    }
}

static PyObject *netsnmp_create_session_v3(PyObject *self, PyObject *args)
{
    int version;
    char *peer;
    int lport;
    int retries;
    int timeout;
    char *sec_name;
    int sec_level;
    char *sec_eng_id;
    char *context_eng_id;
    char *context;
    char *auth_proto;
    char *auth_pass;
    char *priv_proto;
    char *priv_pass;
    int eng_boots;
    int eng_time;
    SnmpSession session = {0};
    SnmpSession *ss = NULL;
    int error = 0;

    if (!PyArg_ParseTuple(args, "isiiisisssssssii", &version,
                          &peer, &lport, &retries, &timeout,
                          &sec_name, &sec_level, &sec_eng_id,
                          &context_eng_id, &context,
                          &auth_proto, &auth_pass,
                          &priv_proto, &priv_pass,
                          &eng_boots, &eng_time))
    {
        return NULL;
    }

    __libraries_init("python");
    snmp_sess_init(&session);

    if (version == 3)
    {
        session.version = SNMP_VERSION_3;
    }
    else
    {
        PyErr_Format(PyExc_ValueError, "unsupported SNMP version (%d)",
                     version);
        error = 1;
        goto end;
    }

    session.peername = peer;
    session.retries = retries; /* 5 */
    session.timeout = timeout; /* 1000000L */
    session.authenticator = NULL;
    session.contextNameLen = STRLEN(context);
    session.contextName = context;
    session.securityNameLen = STRLEN(sec_name);
    session.securityName = sec_name;
    session.securityLevel = sec_level;
    session.securityModel = USM_SEC_MODEL_NUMBER;
    session.securityEngineIDLen =
        hex_to_binary2((unsigned char *)sec_eng_id, STRLEN(sec_eng_id),
                       (char **) &session.securityEngineID);
    session.contextEngineIDLen =
        hex_to_binary2((unsigned char *)context_eng_id, STRLEN(sec_eng_id),
                       (char **) &session.contextEngineID);
    session.engineBoots = eng_boots;
    session.engineTime = eng_time;

#ifndef DISABLE_MD5
    if (!strcmp(auth_proto, "MD5"))
    {
        session.securityAuthProto =
            snmp_duplicate_objid(usmHMACMD5AuthProtocol,
                                 USM_AUTH_PROTO_MD5_LEN);
        session.securityAuthProtoLen = USM_AUTH_PROTO_MD5_LEN;
    }
    else
#endif
    if (!strcmp(auth_proto, "SHA"))
    {
        session.securityAuthProto =
            snmp_duplicate_objid(usmHMACSHA1AuthProtocol,
                                 USM_AUTH_PROTO_SHA_LEN);
        session.securityAuthProtoLen = USM_AUTH_PROTO_SHA_LEN;
    }
    else if (!strcmp(auth_proto, "DEFAULT"))
    {
        const oid* a = get_default_authtype(&session.securityAuthProtoLen);
        session.securityAuthProto
            = snmp_duplicate_objid(a, session.securityAuthProtoLen);
    }
    else
    {
        PyErr_Format(PyExc_ValueError,
                     "unsupported authentication protocol (%s)", auth_proto);
        error = 1;
        goto end;
    }
    if (session.securityLevel >= SNMP_SEC_LEVEL_AUTHNOPRIV)
    {
        if (STRLEN(auth_pass) > 0)
        {
            session.securityAuthKeyLen = USM_AUTH_KU_LEN;
            if (generate_Ku(session.securityAuthProto,
                            session.securityAuthProtoLen,
                            (u_char *)auth_pass, STRLEN(auth_pass),
                            session.securityAuthKey,
                            &session.securityAuthKeyLen) != SNMPERR_SUCCESS)
            {
                PyErr_SetString(EasySNMPConnectionError,
                                "error generating Ku from authentication "
                                "password");
                error = 1;
                goto end;
            }
        }
    }
#ifndef DISABLE_DES
    if (!strcmp(priv_proto, "DES"))
    {
        session.securityPrivProto =
            snmp_duplicate_objid(usmDESPrivProtocol,
                                 USM_PRIV_PROTO_DES_LEN);
        session.securityPrivProtoLen = USM_PRIV_PROTO_DES_LEN;
    }
    else
#endif
    if (!strncmp(priv_proto, "AES", 3))
    {
        session.securityPrivProto =
            snmp_duplicate_objid(usmAESPrivProtocol,
                                 USM_PRIV_PROTO_AES_LEN);
        session.securityPrivProtoLen = USM_PRIV_PROTO_AES_LEN;
    }
    else if (!strcmp(priv_proto, "DEFAULT"))
    {
        const oid *p = get_default_privtype(&session.securityPrivProtoLen);
        session.securityPrivProto =
            snmp_duplicate_objid(p, session.securityPrivProtoLen);
    }
    else
    {
        PyErr_Format(PyExc_ValueError,
                     "unsupported privacy protocol (%s)", priv_proto);
        error = 1;
        goto end;
    }

    if (session.securityLevel >= SNMP_SEC_LEVEL_AUTHPRIV)
    {
        session.securityPrivKeyLen = USM_PRIV_KU_LEN;
        if (generate_Ku(session.securityAuthProto,
                        session.securityAuthProtoLen,
                        (u_char *)priv_pass, STRLEN(priv_pass),
                        session.securityPrivKey,
                        &session.securityPrivKeyLen) != SNMPERR_SUCCESS)
        {
            PyErr_SetString(EasySNMPConnectionError,
                            "couldn't gen Ku from priv pass phrase");
            goto end;
        }
    }

    ss = snmp_sess_open_quiet(&session);

    if (ss == NULL)
    {
        PyErr_Format(EasySNMPConnectionError,
                     "couldn't open SNMP session (%s)",
                     snmp_api_errstring(snmp_errno));
        error = 1;
    }

end:

    free(session.securityEngineID);
    free(session.contextEngineID);

    if (error)
    {
        return NULL;
    }
    else
    {
        return PyLong_FromVoidPtr((void *)ss);
    }
}

static PyObject *netsnmp_create_session_tunneled(PyObject *self,
                                                 PyObject *args)
{
    int version;
    char *peer;
    int lport;
    int retries;
    int timeout;
    char *sec_name;
    int sec_level;
    char *context_eng_id;
    char *context;
    char *our_identity;
    char *their_identity;
    char *their_hostname;
    char *trust_cert;
    SnmpSession session = {0};
    SnmpSession *ss = NULL;
    int error = 0;

    if (!PyArg_ParseTuple(args, "isiiisissssss", &version,
                          &peer, &lport, &retries, &timeout,
                          &sec_name, &sec_level,
                          &context_eng_id, &context,
                          &our_identity, &their_identity,
                          &their_hostname, &trust_cert))
    {
        return NULL;
    }

    if (version != 3)
    {
        PyErr_SetString(PyExc_ValueError,
                        "you must use SNMP version 3 as it's the only "
                        "version that supports tunneling");
        return NULL;
    }

    __libraries_init("python");
    snmp_sess_init(&session);

    session.peername = peer;
    session.retries = retries; /* 5 */
    session.timeout = timeout; /* 1000000L */
    session.contextNameLen = STRLEN(context);
    session.contextName = context;
    session.securityNameLen = STRLEN(sec_name);
    session.securityName = sec_name;
    session.securityLevel = sec_level;
    session.securityModel = NETSNMP_TSM_SECURITY_MODEL;

    /* create the transport configuration store */
    if (!session.transport_configuration)
    {
        netsnmp_container_init_list();
        session.transport_configuration =
            netsnmp_container_find("transport_configuration:fifo");
        if (!session.transport_configuration)
        {
            py_log_msg(ERROR, "failed to initialize the transport "
                              "configuration container");
            return NULL;
        }

        session.transport_configuration->compare =
            (netsnmp_container_compare*) netsnmp_transport_config_compare;
    }

    if (our_identity && our_identity[0] != '\0')
        CONTAINER_INSERT(session.transport_configuration,
                         netsnmp_transport_create_config("localCert",
                                                         our_identity));

    if (their_identity && their_identity[0] != '\0')
        CONTAINER_INSERT(session.transport_configuration,
                         netsnmp_transport_create_config("peerCert",
                                                         their_identity));

    if (their_hostname && their_hostname[0] != '\0')
        CONTAINER_INSERT(session.transport_configuration,
                         netsnmp_transport_create_config("their_hostname",
                                                         their_hostname));

    if (trust_cert && trust_cert[0] != '\0')
        CONTAINER_INSERT(session.transport_configuration,
                         netsnmp_transport_create_config("trust_cert",
                                                         trust_cert));

    ss = snmp_sess_open_quiet(&session);

    if (!ss)
    {
        return NULL;
    }

    /*
     * Note: on a 64-bit system the statement below discards the upper 32
     * bits of "ss", which is most likely a bug.
     */
    if (error)
    {
        return NULL;
    }
    else
    {
        return Py_BuildValue("i", (int)(uintptr_t)ss);
    }
}

static PyObject *netsnmp_delete_session(PyObject *self, PyObject *args)
{
    PyObject *session;
    SnmpSession *ss = NULL;

    if (!PyArg_ParseTuple(args, "O", &session))
    {
        return NULL;
    }

    ss = (SnmpSession *)py_netsnmp_attr_void_ptr(session, "sess_ptr");

    snmp_sess_close(ss);
    return (Py_BuildValue(""));
}

static PyObject *netsnmp_get(PyObject *self, PyObject *args)
{
    PyObject *session;
    PyObject *varlist;
    PyObject *varbind;
    int varlist_len = 0;
    int varlist_ind;
    netsnmp_session *ss;
    netsnmp_pdu *pdu, *response;
    netsnmp_variable_list *vars;
    struct tree *tp;
    int len;
    oid *oid_arr;
    int oid_arr_len = MAX_OID_LEN;
    int type;
    char type_str[MAX_TYPE_NAME_LEN];
    int status;
    u_char str_buf[STR_BUF_SIZE], *str_bufp = str_buf;
    size_t str_buf_len = sizeof(str_buf);
    size_t out_len = 0;
    int buf_over = 0;
    char *tag;
    char *iid;
    int getlabel_flag = NO_FLAGS;
    int sprintval_flag = USE_BASIC;
    int old_format;
    int best_guess;
    int retry_nosuch;
    int err_ind;
    int err_num;
    char err_str[STR_BUF_SIZE];
    char *tmpstr;
    Py_ssize_t tmplen;
    int error = 0;

    oid_arr = calloc(MAX_OID_LEN, sizeof(oid));

    if (oid_arr && args)
    {
        if (!PyArg_ParseTuple(args, "OO", &session, &varlist))
        {
            goto done;
        }

        ss = (SnmpSession *)py_netsnmp_attr_void_ptr(session, "sess_ptr");

        if (py_netsnmp_attr_string(session, "error_string", &tmpstr, &tmplen) < 0)
        {
            goto done;
        }

        if (py_netsnmp_attr_long(session, "use_long_names"))
        {
            getlabel_flag |= USE_LONG_NAMES;
        }
        if (py_netsnmp_attr_long(session, "use_numeric"))
        {
            getlabel_flag |= USE_NUMERIC_OIDS;
        }
        if (py_netsnmp_attr_long(session, "use_enums"))
        {
            sprintval_flag = USE_ENUMS;
        }
        if (py_netsnmp_attr_long(session, "use_sprint_value"))
        {
            sprintval_flag = USE_SPRINT_VALUE;
        }
        best_guess = py_netsnmp_attr_long(session, "best_guess");
        retry_nosuch = py_netsnmp_attr_long(session, "retry_no_such");

        pdu = snmp_pdu_create(SNMP_MSG_GET);

        if (varlist)
        {
            PyObject *varlist_iter = PyObject_GetIter(varlist);

            while (varlist_iter && (varbind = PyIter_Next(varlist_iter)))
            {
                if (py_netsnmp_attr_string(varbind, "oid", &tag, NULL) < 0 ||
                    py_netsnmp_attr_string(varbind, "oid_index", &iid, NULL) < 0)
                {
                    oid_arr_len = 0;
                }
                else
                {
                    tp = __tag2oid(tag, iid, oid_arr, &oid_arr_len, NULL,
                                   best_guess);
                }

                if (oid_arr_len)
                {
                    snmp_add_null_var(pdu, oid_arr, oid_arr_len);
                    varlist_len++;
                }
                else
                {
                    PyErr_Format(EasySNMPUnknownObjectIDError,
                                 "unknown object id (%s)",
                                 (tag ? tag : "<null>"));
                    error = 1;
                    snmp_free_pdu(pdu);
                    Py_DECREF(varbind);
                    goto done;
                }
                /* release reference when done */
                Py_DECREF(varbind);
            }

            Py_DECREF(varlist_iter);

            if (PyErr_Occurred())
            {
                error = 1;
                snmp_free_pdu(pdu);
                goto done;
            }
        }

        status = __send_sync_pdu(ss, pdu, &response, retry_nosuch, err_str,
                                 &err_num, &err_ind);
        __py_netsnmp_update_session_errors(session, err_str, err_num, err_ind);
        if (status != 0)
        {
            error = 1;
            goto done;
        }

        /*
        ** Set up for numeric or full OID's, if necessary.  Save the old
        ** output format so that it can be restored when we finish -- this
        ** is a library-wide global, and has to be set/restored for each
        ** session.
        */
        old_format = netsnmp_ds_get_int(NETSNMP_DS_LIBRARY_ID,
                                        NETSNMP_DS_LIB_OID_OUTPUT_FORMAT);

        if (py_netsnmp_attr_long(session, "use_long_names"))
        {
            getlabel_flag |= USE_LONG_NAMES;

            netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID,
                               NETSNMP_DS_LIB_OID_OUTPUT_FORMAT,
                               NETSNMP_OID_OUTPUT_FULL);
        }
        /* Setting use_numeric forces use_long_names on so check for
          use_numeric after use_long_names (above) to make sure the final
          outcome of NETSNMP_DS_LIB_OID_OUTPUT_FORMAT is
          NETSNMP_OID_OUTPUT_NUMERIC */
        if (py_netsnmp_attr_long(session, "use_numeric"))
        {
            getlabel_flag |= USE_LONG_NAMES;
            getlabel_flag |= USE_NUMERIC_OIDS;

            netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID,
                               NETSNMP_DS_LIB_OID_OUTPUT_FORMAT,
                               NETSNMP_OID_OUTPUT_NUMERIC);
        }

        for (vars = (response ? response->variables : NULL), varlist_ind = 0;
             vars && (varlist_ind < varlist_len);
             vars = vars->next_variable, varlist_ind++)
        {
            varbind = PySequence_GetItem(varlist, varlist_ind);

            if (PyObject_HasAttrString(varbind, "oid"))
            {
                *str_buf = '.';
                *(str_buf + 1) = '\0';
                out_len = 0;
                tp = netsnmp_sprint_realloc_objid_tree(&str_bufp, &str_buf_len,
                                                       &out_len, 0, &buf_over,
                                                       vars->name,
                                                       vars->name_length);

                py_log_msg(DEBUG, "netsnmp_get: str_bufp: %s:%d:%d",
                           str_bufp, (int) str_buf_len, (int) out_len);

                str_buf[sizeof(str_buf) - 1] = '\0';

                if (__is_leaf(tp))
                {
                    type = (tp->type ? tp->type : tp->parent->type);
                    getlabel_flag &= ~NON_LEAF_NAME;
                    py_log_msg(DEBUG, "netsnmp_get: is_leaf: %d", type);
                }
                else
                {
                    getlabel_flag |= NON_LEAF_NAME;
                    type = __translate_asn_type(vars->type);
                    py_log_msg(DEBUG, "netsnmp_get: !is_leaf: %d", tp->type);
                }

                py_log_msg(DEBUG, "netsnmp_get: str_buf: %s", str_buf);

                __get_label_iid((char *) str_buf, &tag, &iid, getlabel_flag);

                py_netsnmp_attr_set_string(varbind, "oid", tag, STRLEN(tag));
                py_netsnmp_attr_set_string(varbind, "oid_index", iid,
                                           STRLEN(iid));

                __get_type_str(type, type_str, 1);

                py_netsnmp_attr_set_string(varbind, "snmp_type", type_str,
                                           strlen(type_str));

                len = __snprint_value((char *) str_buf, sizeof(str_buf),
                                      vars, tp, type, sprintval_flag);
                str_buf[len] = '\0';
                py_netsnmp_attr_set_string(varbind, "value",
                                           (char *) str_buf, len);

                Py_DECREF(varbind);
            }
            else
            {
                py_log_msg(DEBUG, "netsnmp_get: bad varbind (%d)",
                           varlist_ind);
                Py_XDECREF(varbind);
            }
        }

        /* Reset the library's behavior for numeric/symbolic OID's. */
        netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID,
                           NETSNMP_DS_LIB_OID_OUTPUT_FORMAT,
                           old_format);

        if (response)
        {
            snmp_free_pdu(response);
        }
    }

done:

    SAFE_FREE(oid_arr);
    if (error)
    {
        return NULL;
    }
    else
    {
        return Py_None;
    }
}

static PyObject *netsnmp_getnext(PyObject *self, PyObject *args)
{
    PyObject *session;
    PyObject *varlist;
    PyObject *varbind;
    int varlist_len = 0;
    int varlist_ind;
    netsnmp_session *ss;
    netsnmp_pdu *pdu, *response;
    netsnmp_variable_list *vars;
    struct tree *tp;
    int len;
    oid *oid_arr;
    int oid_arr_len = MAX_OID_LEN;
    int type;
    char type_str[MAX_TYPE_NAME_LEN];
    int status;
    u_char str_buf[STR_BUF_SIZE], *str_bufp = str_buf;
    size_t str_buf_len = sizeof(str_buf);
    size_t out_len = 0;
    int buf_over = 0;
    char *tag;
    char *iid = NULL;
    int getlabel_flag = NO_FLAGS;
    int sprintval_flag = USE_BASIC;
    int old_format;
    int best_guess;
    int retry_nosuch;
    int err_ind;
    int err_num;
    char err_str[STR_BUF_SIZE];
    char *tmpstr;
    Py_ssize_t tmplen;
    int error = 0;

    oid_arr = calloc(MAX_OID_LEN, sizeof(oid));

    if (oid_arr && args)
    {
        if (!PyArg_ParseTuple(args, "OO", &session, &varlist))
        {
            goto done;
        }

        ss = (SnmpSession *)py_netsnmp_attr_void_ptr(session, "sess_ptr");

        if (py_netsnmp_attr_string(session, "error_string", &tmpstr, &tmplen) < 0)
        {
            goto done;
        }
        memcpy(&err_str, tmpstr, tmplen);
        err_num = py_netsnmp_attr_long(session, "error_number");
        err_ind = py_netsnmp_attr_long(session, "error_index");

        if (py_netsnmp_attr_long(session, "use_long_names"))
        {
            getlabel_flag |= USE_LONG_NAMES;
        }
        if (py_netsnmp_attr_long(session, "use_numeric"))
        {
            getlabel_flag |= USE_NUMERIC_OIDS;
        }
        if (py_netsnmp_attr_long(session, "use_enums"))
        {
            sprintval_flag = USE_ENUMS;
        }
        if (py_netsnmp_attr_long(session, "use_sprint_value"))
        {
            sprintval_flag = USE_SPRINT_VALUE;
        }
        best_guess = py_netsnmp_attr_long(session, "best_guess");
        retry_nosuch = py_netsnmp_attr_long(session, "retry_no_such");

        pdu = snmp_pdu_create(SNMP_MSG_GETNEXT);

        if (varlist)
        {
            PyObject *varlist_iter = PyObject_GetIter(varlist);

            while (varlist_iter && (varbind = PyIter_Next(varlist_iter)))
            {
                if (py_netsnmp_attr_string(varbind, "oid", &tag, NULL) < 0 ||
                    py_netsnmp_attr_string(varbind, "oid_index", &iid, NULL) < 0)
                {
                    oid_arr_len = 0;
                }
                else
                {
                    tp = __tag2oid(tag, iid, oid_arr, &oid_arr_len, NULL,
                                   best_guess);
                }

                py_log_msg(DEBUG,
                           "netsnmp_getnext: filling request: %s:%s:%d:%d",
                           tag, iid, oid_arr_len, best_guess);

                if (oid_arr_len)
                {
                    snmp_add_null_var(pdu, oid_arr, oid_arr_len);
                    varlist_len++;
                }
                else
                {
                    PyErr_Format(EasySNMPUnknownObjectIDError,
                                 "unknown object id (%s)",
                                 (tag ? tag : "<null>"));
                    error = 1;
                    snmp_free_pdu(pdu);
                    Py_DECREF(varbind);
                    goto done;
                }
                /* release reference when done */
                Py_DECREF(varbind);
            }

            Py_DECREF(varlist_iter);

            if (PyErr_Occurred())
            {
                error = 1;
                snmp_free_pdu(pdu);
                goto done;
            }
        }

        status = __send_sync_pdu(ss, pdu, &response, retry_nosuch, err_str,
                                 &err_num, &err_ind);
        __py_netsnmp_update_session_errors(session, err_str, err_num, err_ind);
        if (status != 0)
        {
            error = 1;
            goto done;
        }

        /*
        ** Set up for numeric or full OID's, if necessary.  Save the old
        ** output format so that it can be restored when we finish -- this
        ** is a library-wide global, and has to be set/restored for each
        ** session.
        */
        old_format = netsnmp_ds_get_int(NETSNMP_DS_LIBRARY_ID,
                                        NETSNMP_DS_LIB_OID_OUTPUT_FORMAT);

        if (py_netsnmp_attr_long(session, "use_long_names"))
        {
            getlabel_flag |= USE_LONG_NAMES;

            netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID,
                               NETSNMP_DS_LIB_OID_OUTPUT_FORMAT,
                               NETSNMP_OID_OUTPUT_FULL);
        }
        /* Setting use_numeric forces use_long_names on so check for
           use_numeric after use_long_names (above) to make sure the final
           outcome of NETSNMP_DS_LIB_OID_OUTPUT_FORMAT is
           NETSNMP_OID_OUTPUT_NUMERIC */
        if (py_netsnmp_attr_long(session, "use_numeric"))
        {
            getlabel_flag |= USE_LONG_NAMES;
            getlabel_flag |= USE_NUMERIC_OIDS;

            netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID,
                               NETSNMP_DS_LIB_OID_OUTPUT_FORMAT,
                               NETSNMP_OID_OUTPUT_NUMERIC);
        }

        for (vars = (response ? response->variables : NULL), varlist_ind = 0;
             vars && (varlist_ind < varlist_len);
             vars = vars->next_variable, varlist_ind++)
        {
            varbind = PySequence_GetItem(varlist, varlist_ind);

            if (PyObject_HasAttrString(varbind, "oid"))
            {
                *str_buf = '.';
                *(str_buf + 1) = '\0';
                out_len = 0;
                tp = netsnmp_sprint_realloc_objid_tree(&str_bufp, &str_buf_len,
                                                       &out_len, 0, &buf_over,
                                                       vars->name,
                                                       vars->name_length);
                str_buf[sizeof(str_buf) - 1] = '\0';

                if (__is_leaf(tp))
                {
                    type = (tp->type ? tp->type : tp->parent->type);
                    getlabel_flag &= ~NON_LEAF_NAME;
                }
                else
                {
                    getlabel_flag |= NON_LEAF_NAME;
                    type = __translate_asn_type(vars->type);
                }

                __get_label_iid((char *) str_buf, &tag, &iid, getlabel_flag);

                py_log_msg(DEBUG, "netsnmp_getnext: filling response: %s:%s",
                           tag, iid);

                py_netsnmp_attr_set_string(varbind, "oid", tag, STRLEN(tag));
                py_netsnmp_attr_set_string(varbind, "oid_index", iid,
                                           STRLEN(iid));

                __get_type_str(type, type_str, 1);

                py_netsnmp_attr_set_string(varbind, "snmp_type", type_str,
                                           strlen(type_str));

                len = __snprint_value((char *) str_buf, sizeof(str_buf),
                                      vars, tp, type, sprintval_flag);
                str_buf[len] = '\0';

                py_netsnmp_attr_set_string(varbind, "value", (char *) str_buf,
                                           len);

                Py_DECREF(varbind);
            }
            else
            {
                py_log_msg(DEBUG, "netsnmp_getnext: bad varbind (%d)",
                           varlist_ind);
                Py_XDECREF(varbind);
            }
        }

        /* Reset the library's behavior for numeric/symbolic OID's. */
        netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID,
                           NETSNMP_DS_LIB_OID_OUTPUT_FORMAT,
                           old_format);

        if (response)
        {
            snmp_free_pdu(response);
        }
    }

done:

    SAFE_FREE(oid_arr);
    if (error)
    {
        return NULL;
    }
    else
    {
        return Py_None;
    }
}

static PyObject *netsnmp_walk(PyObject *self, PyObject *args)
{
    PyObject *session;
    PyObject *varlist;
    PyObject *varlist_iter;
    PyObject *varbind;
    PyObject *varbinds  = NULL;
    int varlist_len = 0;
    int varlist_ind;
    netsnmp_session *ss;
    netsnmp_pdu *pdu, *response;
    netsnmp_pdu *newpdu;
    netsnmp_variable_list *vars, *oldvars;
    struct tree *tp;
    int len;
    oid **oid_arr = NULL;
    int *oid_arr_len = NULL;
    oid **oid_arr_broken_check = NULL;
    int *oid_arr_broken_check_len = NULL;
    int type;
    char type_str[MAX_TYPE_NAME_LEN];
    int status;
    u_char str_buf[STR_BUF_SIZE], *str_bufp = str_buf;
    size_t str_buf_len = sizeof(str_buf);
    size_t out_len = 0;
    int buf_over = 0;
    char *tag;
    char *iid = NULL;
    int getlabel_flag = NO_FLAGS;
    int sprintval_flag = USE_BASIC;
    int old_format;
    int best_guess;
    int retry_nosuch;
    int err_ind;
    int err_num;
    char err_str[STR_BUF_SIZE];
    int notdone = 1;
    char *tmpstr;
    Py_ssize_t tmplen;
    int error = 0;

    if (args)
    {
        if (!PyArg_ParseTuple(args, "OO", &session, &varlist))
        {
            goto done;
        }

        if (!varlist)
        {
            goto done;
        }

        if ((varbinds = PyObject_GetAttrString(varlist, "varbinds")) == NULL)
        {
            goto done;
        }
        ss = (SnmpSession *)py_netsnmp_attr_void_ptr(session, "sess_ptr");

        if (py_netsnmp_attr_string(session, "error_string", &tmpstr, &tmplen) < 0)
        {
            goto done;
        }
        memcpy(&err_str, tmpstr, tmplen);
        err_num = py_netsnmp_attr_long(session, "error_number");
        err_ind = py_netsnmp_attr_long(session, "error_index");

        if (py_netsnmp_attr_long(session, "use_long_names"))
        {
            getlabel_flag |= USE_LONG_NAMES;
        }
        if (py_netsnmp_attr_long(session, "use_numeric"))
        {
            getlabel_flag |= USE_NUMERIC_OIDS;
        }
        if (py_netsnmp_attr_long(session, "use_enums"))
        {
            sprintval_flag = USE_ENUMS;
        }
        if (py_netsnmp_attr_long(session, "use_sprint_value"))
        {
            sprintval_flag = USE_SPRINT_VALUE;
        }
        best_guess = py_netsnmp_attr_long(session, "best_guess");
        retry_nosuch = py_netsnmp_attr_long(session, "retry_no_such");

        pdu = snmp_pdu_create(SNMP_MSG_GETNEXT);

        /* we need an initial count for memory allocation */
        varlist_iter = PyObject_GetIter(varlist);
        varlist_len = 0;
        while (varlist_iter && (varbind = PyIter_Next(varlist_iter)))
        {
            varlist_len++;
        }
        Py_DECREF(varlist_iter);

        oid_arr_len              = calloc(varlist_len, sizeof(int));
        oid_arr_broken_check_len = calloc(varlist_len, sizeof(int));

        oid_arr                  = calloc(varlist_len, sizeof(oid *));
        oid_arr_broken_check     = calloc(varlist_len, sizeof(oid *));

        for (varlist_ind = 0; varlist_ind < varlist_len; varlist_ind++)
        {
            oid_arr[varlist_ind] = calloc(MAX_OID_LEN, sizeof(oid));
            oid_arr_broken_check[varlist_ind] = calloc(MAX_OID_LEN,
                                                       sizeof(oid));

            oid_arr_len[varlist_ind]              = MAX_OID_LEN;
            oid_arr_broken_check_len[varlist_ind] = MAX_OID_LEN;
        }

        /* get the initial starting oids */
        varlist_iter = PyObject_GetIter(varlist);
        varlist_ind = 0;
        while (varlist_iter && (varbind = PyIter_Next(varlist_iter)))
        {
            if (py_netsnmp_attr_string(varbind, "oid", &tag, NULL) < 0 ||
                py_netsnmp_attr_string(varbind, "oid_index", &iid, NULL) < 0)
            {
                oid_arr_len[varlist_ind] = 0;
            }
            else
            {
                tp = __tag2oid(tag, iid,
                               oid_arr[varlist_ind], &oid_arr_len[varlist_ind],
                               NULL, best_guess);
            }

            if (oid_arr_len[varlist_ind])
            {
                py_log_msg(DEBUG, "netsnmp_walk: filling request: %s:%s:%d:%d",
                           tag, iid, oid_arr_len[varlist_ind], best_guess);

                snmp_add_null_var(pdu, oid_arr[varlist_ind],
                                  oid_arr_len[varlist_ind]);
            }
            else
            {
                PyErr_Format(EasySNMPUnknownObjectIDError,
                             "unknown object id (%s)",
                             (tag ? tag : "<null>"));
                error = 1;
                snmp_free_pdu(pdu);
                Py_DECREF(varbind);
                goto done;
            }
            /* release reference when done */
            Py_DECREF(varbind);
            varlist_ind++;
        }

        if (varlist_iter)
        {
            Py_DECREF(varlist_iter);
        }

        if (PyErr_Occurred())
        {
            error = 1;
            snmp_free_pdu(pdu);
            goto done;
        }

        if (PyErr_Occurred())
        {
            error = 1;
            snmp_free_pdu(pdu);
            goto done;
        }

        /*
        ** Set up for numeric or full OID's, if necessary.  Save the old
        ** output format so that it can be restored when we finish -- this
        ** is a library-wide global, and has to be set/restored for each
        ** session.
        */
        old_format = netsnmp_ds_get_int(NETSNMP_DS_LIBRARY_ID,
                                        NETSNMP_DS_LIB_OID_OUTPUT_FORMAT);

        if (py_netsnmp_attr_long(session, "use_long_names"))
        {
            getlabel_flag |= USE_LONG_NAMES;

            netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID,
                               NETSNMP_DS_LIB_OID_OUTPUT_FORMAT,
                               NETSNMP_OID_OUTPUT_FULL);
        }

        /* Setting use_numeric forces use_long_names on so check for
           use_numeric after use_long_names (above) to make sure the final
           outcome of NETSNMP_DS_LIB_OID_OUTPUT_FORMAT is
           NETSNMP_OID_OUTPUT_NUMERIC */
        if (py_netsnmp_attr_long(session, "use_numeric"))
        {
            getlabel_flag |= USE_LONG_NAMES;
            getlabel_flag |= USE_NUMERIC_OIDS;

            netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID,
                               NETSNMP_DS_LIB_OID_OUTPUT_FORMAT,
                               NETSNMP_OID_OUTPUT_NUMERIC);
        }

        /* delete the existing varbinds that we'll replace */
        PySequence_DelSlice(varbinds, 0, PySequence_Length(varbinds));

        if (PyErr_Occurred())
        {
            error = 1;
            snmp_free_pdu(pdu);
            goto done;
        }

        /* save the starting OID */

        for (vars = pdu->variables, varlist_ind = 0;
             vars != NULL;
             vars = vars->next_variable, varlist_ind++)
        {
            oid_arr_broken_check[varlist_ind] =
                calloc(MAX_OID_LEN, sizeof(oid));

            oid_arr_broken_check_len[varlist_ind] = vars->name_length;
            memcpy(oid_arr_broken_check[varlist_ind],
                   vars->name, vars->name_length * sizeof(oid));
        }

        while (notdone) {
            status = __send_sync_pdu(ss, pdu, &response, retry_nosuch,
                                     err_str, &err_num, &err_ind);
            __py_netsnmp_update_session_errors(session, err_str, err_num,
                                               err_ind);
            if (status != 0)
            {
                error = 1;
                goto done;
            }

            if (!response || !response->variables ||
                status != STAT_SUCCESS ||
                response->errstat != SNMP_ERR_NOERROR)
            {
                notdone = 0;
            }
            else
            {
                newpdu = snmp_pdu_create(SNMP_MSG_GETNEXT);

                for (vars = (response ? response->variables : NULL),
                     varlist_ind = 0,
                     oldvars = (pdu ? pdu->variables : NULL);
                     vars && (varlist_ind < varlist_len);
                     vars = vars->next_variable, varlist_ind++,
                     oldvars = (oldvars ? oldvars->next_variable : NULL))
                {
                    if ((vars->name_length < oid_arr_len[varlist_ind]) ||
                        (memcmp(oid_arr[varlist_ind], vars->name,
                                oid_arr_len[varlist_ind] * sizeof(oid)) != 0))
                    {
                        notdone = 0;
                        break;
                    }

                    if ((vars->type == SNMP_ENDOFMIBVIEW) ||
                        (vars->type == SNMP_NOSUCHOBJECT) ||
                        (vars->type == SNMP_NOSUCHINSTANCE))
                    {
                        notdone = 0;
                        break;
                    }

                    if (snmp_oid_compare(vars->name, vars->name_length,
                                         oid_arr_broken_check[varlist_ind],
                                         oid_arr_broken_check_len[varlist_ind]) <= 0)
                    {
                        /* The agent responded with an illegal response
                           as the returning OID was lexogragically less
                           then or equal to the requested OID...
                           We need to give up here because an infite
                           loop will result otherwise.

                           XXX: this really should be an option to
                           continue like the -Cc option to the snmpwalk
                           application.
                        */
                        notdone = 0;
                        break;
                    }

                    varbind = py_netsnmp_construct_varbind();

                    if (PyObject_HasAttrString(varbind, "oid"))
                    {
                        str_buf[0] = '.';
                        str_buf[1] = '\0';
                        out_len = 0;
                        tp = netsnmp_sprint_realloc_objid_tree(&str_bufp,
                                                               &str_buf_len,
                                                               &out_len, 0,
                                                               &buf_over,
                                                               vars->name,
                                                               vars->name_length);
                        str_buf[sizeof(str_buf) - 1] = '\0';

                        if (__is_leaf(tp))
                        {
                            type = (tp->type ? tp->type : tp->parent->type);
                            getlabel_flag &= ~NON_LEAF_NAME;
                        }
                        else
                        {
                            getlabel_flag |= NON_LEAF_NAME;
                            type = __translate_asn_type(vars->type);
                        }

                        __get_label_iid((char *) str_buf, &tag, &iid,
                                        getlabel_flag);

                        py_log_msg(DEBUG,
                                   "netsnmp_walk: filling response: %s:%s",
                                   tag, iid);

                        py_netsnmp_attr_set_string(varbind, "oid", tag,
                                                   STRLEN(tag));
                        py_netsnmp_attr_set_string(varbind, "oid_index", iid,
                                                   STRLEN(iid));

                        __get_type_str(type, type_str, 1);

                        py_netsnmp_attr_set_string(varbind, "snmp_type",
                                                   type_str, strlen(type_str));

                        len = __snprint_value((char *) str_buf,
                                              sizeof(str_buf), vars, tp,
                                              type, sprintval_flag);
                        str_buf[len] = '\0';

                        py_netsnmp_attr_set_string(varbind, "value",
                                                   (char *) str_buf, len);

                        /* push the varbind onto the return varbinds */
                        PyList_Append(varbinds, varbind);
                    }
                    else
                    {
                        py_log_msg(DEBUG, "netsnmp_walk: bad varbind (%d)",
                                   varlist_ind);
                    }
                    Py_XDECREF(varbind);

                    memcpy(oid_arr_broken_check[varlist_ind], vars->name,
                           sizeof(oid) * vars->name_length);
                    oid_arr_broken_check_len[varlist_ind] = vars->name_length;

                    snmp_add_null_var(newpdu, vars->name, vars->name_length);
                }
                pdu = newpdu;
            }
            if (response)
            {
                snmp_free_pdu(response);
            }
        }

        /* Reset the library's behavior for numeric/symbolic OID's. */
        netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID,
                           NETSNMP_DS_LIB_OID_OUTPUT_FORMAT,
                           old_format);


        if (PyErr_Occurred())
        {
            error = 1;
        }
    }

done:

    Py_XDECREF(varbinds);
    SAFE_FREE(oid_arr_len);
    SAFE_FREE(oid_arr_broken_check_len);
    for (varlist_ind = 0; varlist_ind < varlist_len; varlist_ind++)
    {
        SAFE_FREE(oid_arr[varlist_ind]);
        SAFE_FREE(oid_arr_broken_check[varlist_ind]);
    }
    SAFE_FREE(oid_arr);
    SAFE_FREE(oid_arr_broken_check);
    if (error)
    {
        return NULL;
    }
    else
    {
        return Py_None;
    }
}

static PyObject *netsnmp_getbulk(PyObject *self, PyObject *args)
{
    int nonrepeaters;
    int maxrepetitions;
    PyObject *session;
    PyObject *varlist;
    PyObject *varbinds;
    PyObject *varbind;
    PyObject *varbinds_iter;
    int varbind_ind;
    netsnmp_session *ss;
    netsnmp_pdu *pdu, *response;
    netsnmp_variable_list *vars;
    struct tree *tp;
    int len;
    oid *oid_arr;
    int oid_arr_len = MAX_OID_LEN;
    int type;
    char type_str[MAX_TYPE_NAME_LEN];
    int status;
    u_char str_buf[STR_BUF_SIZE], *str_bufp = str_buf;
    size_t str_buf_len = sizeof(str_buf);
    size_t out_len = 0;
    int buf_over = 0;
    char *tag;
    char *iid;
    int getlabel_flag = NO_FLAGS;
    int sprintval_flag = USE_BASIC;
    int old_format;
    int best_guess;
    int retry_nosuch;
    int err_ind;
    int err_num;
    char err_str[STR_BUF_SIZE];
    char *tmpstr;
    Py_ssize_t tmplen;
    int error = 0;

    oid_arr = calloc(MAX_OID_LEN, sizeof(oid));

    if (oid_arr && args)
    {
        if (!PyArg_ParseTuple(args, "OiiO", &session, &nonrepeaters,
                              &maxrepetitions, &varlist))
        {
            goto done;
        }

        if (varlist &&
            (varbinds = PyObject_GetAttrString(varlist, "varbinds")))
        {
            ss = (SnmpSession *)py_netsnmp_attr_void_ptr(session, "sess_ptr");

            if (py_netsnmp_attr_string(session, "error_string", &tmpstr, &tmplen) < 0)
            {
                goto done;
            }
            memcpy(&err_str, tmpstr, tmplen);
            err_num = py_netsnmp_attr_long(session, "error_number");
            err_ind = py_netsnmp_attr_long(session, "error_index");

            if (py_netsnmp_attr_long(session, "use_long_names"))
            {
                getlabel_flag |= USE_LONG_NAMES;
            }
            if (py_netsnmp_attr_long(session, "use_numeric"))
            {
                getlabel_flag |= USE_NUMERIC_OIDS;
            }
            if (py_netsnmp_attr_long(session, "use_enums"))
            {
                sprintval_flag = USE_ENUMS;
            }
            if (py_netsnmp_attr_long(session, "use_sprint_value"))
            {
                sprintval_flag = USE_SPRINT_VALUE;
            }
            best_guess = py_netsnmp_attr_long(session, "best_guess");
            retry_nosuch = py_netsnmp_attr_long(session, "retry_no_such");

            pdu = snmp_pdu_create(SNMP_MSG_GETBULK);

            pdu->errstat = nonrepeaters;
            pdu->errindex = maxrepetitions;

            varbinds_iter = PyObject_GetIter(varbinds);

            while (varbinds_iter && (varbind = PyIter_Next(varbinds_iter)))
            {
                if (py_netsnmp_attr_string(varbind, "oid", &tag, NULL) < 0 ||
                    py_netsnmp_attr_string(varbind, "oid_index", &iid, NULL) < 0)
                {
                    oid_arr_len = 0;
                }
                else
                {
                    tp = __tag2oid(tag, iid, oid_arr, &oid_arr_len, NULL,
                                   best_guess);
                }

                if (oid_arr_len)
                {
                    snmp_add_null_var(pdu, oid_arr, oid_arr_len);
                }
                else
                {
                    PyErr_Format(EasySNMPUnknownObjectIDError,
                                 "unknown object id (%s)",
                                 (tag ? tag : "<null>"));
                    error = 1;
                    snmp_free_pdu(pdu);
                    Py_DECREF(varbind);
                    goto done;
                }
                /* release reference when done */
                Py_DECREF(varbind);
            }

            Py_DECREF(varbinds_iter);

            if (PyErr_Occurred())
            {
                error = 1;
                snmp_free_pdu(pdu);
                goto done;
            }

            status = __send_sync_pdu(ss, pdu, &response, retry_nosuch,
                                     err_str, &err_num, &err_ind);
            __py_netsnmp_update_session_errors(session, err_str, err_num,
                                               err_ind);
            if (status != 0)
            {
                error = 1;
                goto done;
            }

            /*
            ** Set up for numeric or full OID's, if necessary.  Save the old
            ** output format so that it can be restored when we finish -- this
            ** is a library-wide global, and has to be set/restored for each
            ** session.
            */
            old_format = netsnmp_ds_get_int(NETSNMP_DS_LIBRARY_ID,
                                            NETSNMP_DS_LIB_OID_OUTPUT_FORMAT);

            if (py_netsnmp_attr_long(session, "use_long_names"))
            {
                getlabel_flag |= USE_LONG_NAMES;

                netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID,
                                   NETSNMP_DS_LIB_OID_OUTPUT_FORMAT,
                                   NETSNMP_OID_OUTPUT_FULL);
            }
            /* Setting use_numeric forces use_long_names on so check for
               use_numeric after use_long_names (above) to make sure the final
               outcome of NETSNMP_DS_LIB_OID_OUTPUT_FORMAT is
               NETSNMP_OID_OUTPUT_NUMERIC */
            if (py_netsnmp_attr_long(session, "use_numeric"))
            {
                getlabel_flag |= USE_LONG_NAMES;
                getlabel_flag |= USE_NUMERIC_OIDS;

                netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID,
                                   NETSNMP_DS_LIB_OID_OUTPUT_FORMAT,
                                   NETSNMP_OID_OUTPUT_NUMERIC);
            }

            if(response && response->variables)
            {
                /* clear varlist to receive response varbinds*/
                PySequence_DelSlice(varbinds, 0, PySequence_Length(varbinds));

                if (PyErr_Occurred())
                {
                    error = 1;
                    snmp_free_pdu(pdu);
                    goto done;
                }

                for (vars = response->variables, varbind_ind=0;
                     vars;
                     vars = vars->next_variable, varbind_ind++)
                {

                    varbind = py_netsnmp_construct_varbind();

                    if (PyObject_HasAttrString(varbind, "oid"))
                    {
                        *str_buf = '.';
                        *(str_buf + 1) = '\0';
                        out_len = 0;
                        buf_over = 0;
                        str_bufp = str_buf;
                        tp = netsnmp_sprint_realloc_objid_tree(&str_bufp,
                                                               &str_buf_len,
                                                               &out_len, 0,
                                                               &buf_over,
                                                               vars->name,
                                                               vars->name_length);
                        str_buf[sizeof(str_buf) - 1] = '\0';
                        if (__is_leaf(tp))
                        {
                            type = (tp->type ? tp->type : tp->parent->type);
                            getlabel_flag &= ~NON_LEAF_NAME;
                        }
                        else
                        {
                            getlabel_flag |= NON_LEAF_NAME;
                            type = __translate_asn_type(vars->type);
                        }

                        __get_label_iid((char *) str_buf, &tag, &iid,
                                        getlabel_flag);

                        py_netsnmp_attr_set_string(varbind, "oid", tag,
                                                   STRLEN(tag));
                        py_netsnmp_attr_set_string(varbind, "oid_index", iid,
                                                   STRLEN(iid));

                        __get_type_str(type, type_str, 1);

                        py_netsnmp_attr_set_string(varbind, "snmp_type",
                                                   type_str, strlen(type_str));

                        len = __snprint_value((char *) str_buf,
                                              sizeof(str_buf), vars, tp, type,
                                              sprintval_flag);
                        str_buf[len] = '\0';

                        py_netsnmp_attr_set_string(varbind, "value",
                                                   (char *) str_buf, len);

                        /* push varbind onto varbinds */
                        PyList_Append(varbinds, varbind);

                        Py_DECREF(varbind);
                    }
                    else
                    {
                        PyObject *none = Py_BuildValue(""); /* new ref */
                        /* not sure why making vabind failed - should not happen*/
                        PyList_Append(varbinds, none); /* increments ref */
                        /* Return None for this variable. */
                        Py_XDECREF(varbind);
                    }
                }
            }

            /* Reset the library's behavior for numeric/symbolic OID's. */
            netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID,
                               NETSNMP_DS_LIB_OID_OUTPUT_FORMAT,
                               old_format);

            if (response)
            {
                snmp_free_pdu(response);
            }

            Py_DECREF(varbinds);
        }

        if (PyErr_Occurred())
        {
            error = 1;
        }
    }

done:

    SAFE_FREE(oid_arr);
    if (error)
    {
        return NULL;
    }
    else
    {
        return Py_None;
    }
}

static PyObject *netsnmp_set(PyObject *self, PyObject *args)
{
    PyObject *session;
    PyObject *varlist;
    PyObject *varbind;
    PyObject *ret = NULL;
    netsnmp_session *ss;
    netsnmp_pdu *pdu, *response;
    struct tree *tp;
    char *tag;
    char *iid;
    char *val;
    char *type_str;
    int len;
    oid *oid_arr;
    int oid_arr_len = MAX_OID_LEN;
    int type;
    u_char tmp_val_str[STR_BUF_SIZE];
    int use_enums;
    struct enum_list *ep;
    int best_guess;
    int status;
    int err_ind;
    int err_num;
    char err_str[STR_BUF_SIZE];
    char *tmpstr;
    Py_ssize_t tmplen;
    int error = 0;

    oid_arr = calloc(MAX_OID_LEN, sizeof(oid));

    if (oid_arr && args)
    {
        if (!PyArg_ParseTuple(args, "OO", &session, &varlist))
        {
            goto done;
        }

        ss = (SnmpSession *)py_netsnmp_attr_void_ptr(session, "sess_ptr");

        /* PyObject_SetAttrString(); */
        if (py_netsnmp_attr_string(session, "error_string", &tmpstr, &tmplen) < 0)
        {
            goto done;
        }

        use_enums = py_netsnmp_attr_long(session, "use_enums");

        best_guess = py_netsnmp_attr_long(session, "best_guess");

        pdu = snmp_pdu_create(SNMP_MSG_SET);

        if (varlist)
        {
            PyObject *varlist_iter = PyObject_GetIter(varlist);

            while (varlist_iter && (varbind = PyIter_Next(varlist_iter)))
            {
                if (py_netsnmp_attr_string(varbind, "oid", &tag, NULL) < 0 ||
                    py_netsnmp_attr_string(varbind, "oid_index", &iid, NULL) < 0)
                {
                    oid_arr_len = 0;
                }
                else
                {
                    tp = __tag2oid(tag, iid, oid_arr, &oid_arr_len, &type,
                                   best_guess);
                }

                if (oid_arr_len==0)
                {
                    PyErr_Format(EasySNMPUnknownObjectIDError,
                                 "unknown object id (%s)",
                                 (tag ? tag : "<null>"));
                    error = 1;
                    snmp_free_pdu(pdu);
                    goto done;
                }

                if (type == TYPE_UNKNOWN)
                {
                    if (py_netsnmp_attr_string(varbind, "snmp_type", &type_str, NULL) < 0)
                    {
                        snmp_free_pdu(pdu);
                        goto done;
                    }
                    type = __translate_appl_type(type_str);
                    if (type == TYPE_UNKNOWN)
                    {
                        PyErr_SetString(EasySNMPUndeterminedTypeError,
                                        "a type could not be determine for "
                                        "the object");
                        error = 1;
                        snmp_free_pdu(pdu);
                        goto done;
                    }
                }

                if (py_netsnmp_attr_string(varbind, "value", &val, &tmplen) < 0)
                {
                    snmp_free_pdu(pdu);
                    goto done;
                }
                memset(tmp_val_str, 0, sizeof(tmp_val_str));
                if (tmplen >= sizeof(tmp_val_str))
                {
                    tmplen = sizeof(tmp_val_str) - 1;
                }
                memcpy(tmp_val_str, val, tmplen);
                if (type == TYPE_INTEGER && use_enums && tp && tp->enums)
                {
                    for (ep = tp->enums; ep; ep = ep->next)
                    {
                        if (val && !strcmp(ep->label, val))
                        {
                            snprintf((char *) tmp_val_str, sizeof(tmp_val_str),
                                     "%d", ep->value);
                            break;
                        }
                    }
                }
                len = (int)tmplen;
                status = __add_var_val_str(pdu, oid_arr, oid_arr_len,
                                           (char *) tmp_val_str, len, type);

                if (status == FAILURE)
                {
                    py_log_msg(ERROR, "set: adding variable/value to PDU");
                }

                /* release reference when done */
                Py_DECREF(varbind);
            }

            Py_DECREF(varlist_iter);

            if (PyErr_Occurred())
            {
                error = 1;
                snmp_free_pdu(pdu);
                goto done;
            }
        }

        status = __send_sync_pdu(ss, pdu, &response, NO_RETRY_NOSUCH,
                                 err_str, &err_num, &err_ind);
        __py_netsnmp_update_session_errors(session, err_str, err_num, err_ind);
        if (status != 0)
        {
            error = 1;
            goto done;
        }

        if (response)
        {
            snmp_free_pdu(response);
        }

        if (status == STAT_SUCCESS)
        {
            ret = Py_BuildValue("i", 1); /* success, return True */
        }
        else
        {
            ret = Py_BuildValue("i", 0); /* fail, return False */
        }
    }

done:

    Py_XDECREF(varbind);
    SAFE_FREE(oid_arr);
    if (error)
    {
        return NULL;
    }
    else
    {
        return (ret ? ret : Py_BuildValue(""));
    }
}

/**
 * Get a logger object from the logging module.
 */
static PyObject *py_get_logger(char *logger_name)
{
    PyObject *logger = NULL;
    PyObject *null_handler = NULL;

    logger = PyObject_CallMethod(logging_import, "getLogger", "s", logger_name);
    if (logger == NULL)
    {
        const char *err_msg = "failed to call logging.getLogger";
        PyErr_SetString(PyExc_RuntimeError, err_msg);
        goto done;
    }

    /*
     * Since this is a library module, a handler needs to be configured when
     * logging; otherwise a warning is emitted to stderr.
     *
     * https://docs.python.org/3.4/howto/logging.html#library-config recommends:
     * >>> logging.getLogger('foo').addHandler(logging.NullHandler())
     *
     * However NullHandler doesn't come with python <2.6 and <3.1, so we need
     * to improvise by using an identical copy in easysnmp.compat.
     *
     */

    null_handler = PyObject_CallMethod(easysnmp_compat_import, "NullHandler", NULL);
    if (null_handler == NULL)
    {
        const char *err_msg = "failed to call easysnmp.compat.NullHandler()";
        PyErr_SetString(PyExc_RuntimeError, err_msg);
        goto done;
    }

    if (PyObject_CallMethod(logger, "addHandler", "O", null_handler) == NULL)
    {
        const char *err_msg = "failed to call logger.addHandler(NullHandler())";
        PyErr_SetString(PyExc_RuntimeError, err_msg);
        goto done;
    }

    /* we don't need the null_handler around anymore. */
    Py_DECREF(null_handler);

    return logger;

done:

    Py_XDECREF(logger);
    Py_XDECREF(null_handler);

    return NULL;
}

static void py_log_msg(int log_level, char *printf_fmt, ...)
{
    PyObject *log_msg = NULL;
    va_list fmt_args;

    va_start(fmt_args, printf_fmt);
    log_msg = PyUnicode_FromFormatV(printf_fmt, fmt_args);
    va_end(fmt_args);

    if (log_msg == NULL)
    {
        /* fail silently. */
        return;
    }

    /* call function depending on loglevel */
    switch (log_level)
    {
        case INFO:
            PyObject_CallMethod(PyLogger, "info", "O", log_msg);
            break;

        case WARNING:
            PyObject_CallMethod(PyLogger, "warn", "O", log_msg);
            break;

        case ERROR:
            PyObject_CallMethod(PyLogger, "error", "O", log_msg);
            break;

        case DEBUG:
            PyObject_CallMethod(PyLogger, "debug", "O", log_msg);
            break;

        case EXCEPTION:
            PyObject_CallMethod(PyLogger, "exception", "O", log_msg);
            break;

        default:
            break;
    }

    Py_DECREF(log_msg);
}

/*
 * Array of defined methods when initialising the module,
 * each entry must contain the following:
 *
 *     (char *)      ml_name:   name of method
 *     (PyCFunction) ml_meth:   pointer to the C implementation
 *     (int)         ml_flags:  flag bit indicating how call should be
 *     (char *)      ml_doc:    points to contents of method docstring
 *
 * See: https://docs.python.org/2/c-api/structures.html for more info.
 *
 */
static PyMethodDef interface_methods[] =
    {
        {
            "session",
            netsnmp_create_session,
            METH_VARARGS,
            "create a netsnmp session."
        },
        {
            "session_v3",
            netsnmp_create_session_v3,
            METH_VARARGS,
            "create a netsnmp session."
        },
        {
            "session_tunneled",
            netsnmp_create_session_tunneled,
            METH_VARARGS,
            "create a tunneled netsnmp session over tls, dtls or ssh."
        },
        {
            "delete_session",
            netsnmp_delete_session,
            METH_VARARGS,
            "create a netsnmp session."
        },
        {
            "get",
            netsnmp_get,
            METH_VARARGS,
            "perform an SNMP GET operation."
        },
        {
            "getnext",
            netsnmp_getnext,
            METH_VARARGS,
            "perform an SNMP GETNEXT operation."
        },
        {
            "getbulk",
            netsnmp_getbulk,
            METH_VARARGS,
            "perform an SNMP GETBULK operation."
        },
        {
            "set",
            netsnmp_set,
            METH_VARARGS,
            "perform an SNMP SET operation."
        },
        {
            "walk",
            netsnmp_walk,
            METH_VARARGS,
            "perform an SNMP WALK operation."
        },
        {
            NULL,
            NULL,
            0,
            NULL
        } /* Sentinel */
    };

/* entry point when importing the module */
#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "interface",
    NULL,
    -1,
    interface_methods
};

PyMODINIT_FUNC PyInit_interface(void)
{
    /* Initialise the module */
    PyObject *interface_module = PyModule_Create(&moduledef);

#else

PyMODINIT_FUNC initinterface(void)
{
    /* Initialise the module */
    PyObject *interface_module = Py_InitModule("interface", interface_methods);

#endif
    if (interface_module == NULL)
    {
        goto done;
    }

    /*
     * Perform global imports:
     *
     * import logging
     * import easysnmp
     * import easysnmp.exceptions
     * import easysnmp.compat
     *
     */
    logging_import = PyImport_ImportModule("logging");
    if (logging_import == NULL)
    {
        const char *err_msg = "failed to import 'logging'";
        PyErr_SetString(PyExc_ImportError, err_msg);
        goto done;
    }

    easysnmp_import = PyImport_ImportModule("easysnmp");
    if (easysnmp_import == NULL)
    {
        const char *err_msg = "failed to import 'easysnmp'";
        PyErr_SetString(PyExc_ImportError, err_msg);
        goto done;
    }

    easysnmp_exceptions_import = PyImport_ImportModule("easysnmp.exceptions");
    if (easysnmp_exceptions_import == NULL)
    {
        const char *err_msg = "failed to import 'easysnmp.exceptions'";
        PyErr_SetString(PyExc_ImportError, err_msg);
        goto done;
    }

    easysnmp_compat_import = PyImport_ImportModule("easysnmp.compat");
    if (easysnmp_compat_import == NULL)
    {
        const char *err_msg = "failed to import 'easysnmp.compat'";
        PyErr_SetString(PyExc_ImportError, err_msg);
        goto done;
    }

    EasySNMPError = PyObject_GetAttrString(easysnmp_exceptions_import, "EasySNMPError");
    EasySNMPConnectionError = PyObject_GetAttrString(easysnmp_exceptions_import,
                                                     "EasySNMPConnectionError");
    EasySNMPTimeoutError = PyObject_GetAttrString(easysnmp_exceptions_import,
                                                  "EasySNMPTimeoutError");
    EasySNMPUnknownObjectIDError = PyObject_GetAttrString(easysnmp_exceptions_import,
                                                          "EasySNMPUnknownObjectIDError");
    EasySNMPNoSuchObjectError = PyObject_GetAttrString(easysnmp_exceptions_import,
                                                       "EasySNMPNoSuchObjectError");
    EasySNMPUndeterminedTypeError = PyObject_GetAttrString(easysnmp_exceptions_import,
                                                           "EasySNMPUndeterminedTypeError");

    /* Initialise logging (note: automatically has refcount 1) */
    PyLogger = py_get_logger("easysnmp.interface");

    if (PyLogger == NULL)
    {
        goto done;
    }

    py_log_msg(DEBUG, "initialised easysnmp.interface");

#if PY_MAJOR_VERSION >= 3
    return interface_module;
#else
    return;
#endif

done:
    Py_XDECREF(interface_module);
    Py_XDECREF(logging_import);
    Py_XDECREF(easysnmp_import);
    Py_XDECREF(easysnmp_exceptions_import);
    Py_XDECREF(easysnmp_compat_import);
    Py_XDECREF(EasySNMPError);
    Py_XDECREF(EasySNMPConnectionError);
    Py_XDECREF(EasySNMPTimeoutError);
    Py_XDECREF(EasySNMPUnknownObjectIDError);
    Py_XDECREF(EasySNMPNoSuchObjectError);
    Py_XDECREF(EasySNMPUndeterminedTypeError);
    Py_XDECREF(PyLogger);

#if PY_MAJOR_VERSION >= 3
    return NULL;
#else
    return;
#endif
}
