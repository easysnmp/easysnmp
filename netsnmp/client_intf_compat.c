/* This file provides backwards compatibility for
 * versions of Net-SNMP older than 5.7.3 which do not
 * have netsnmp_memdup().
 */

#include <stdlib.h>
#include <string.h>

/**
 * Duplicates a memory block.
 *
 * @param[in] from Pointer to copy memory from.
 * @param[in] size Size of the data to be copied.
 *
 * @return Pointer to the duplicated memory block, or NULL if memory allocation
 * failed.
 */
void *netsnmp_memdup(const void *from, size_t size)
{
    void *to = NULL;

    if (from) {
        to = malloc(size);
        if (to)
            memcpy(to, from, size);
    }
    return to;
}                               /* end netsnmp_memdup() */
