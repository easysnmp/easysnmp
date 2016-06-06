#ifndef SIMPLE_BITARRAY_H
#define SIMPLE_BITARRAY_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if (__STDC_VERSION__ < 199901L)
#define inline
#endif

/*
 * No weird architectures; we expect the following:
 *   - a byte to be 8 bits (i.e. CHAR_BIT == 8)
 *   - integral types do not have padding or reserved bits
 *     e.g. if sizeof(unsigned int) == 4 then UINT_MAX == 4294967295
 */
typedef unsigned int bitarray;

/*
 * This is not guaranteed to be portable since an integral type size
 * dosn't necessarily define the range. See warning above about
 * "no weird architectures."
 */
#define BITARRAY_LIMB_BITS (sizeof(bitarray) * CHAR_BIT)

/* macro to find the number of limbs to store num-bits */
#define BITARRAY_NUM_BITS_TO_LIMBS(num_bits) \
    (((num_bits) + BITARRAY_LIMB_BITS - 1) / BITARRAY_LIMB_BITS)

/* macro to find the number of limbs to store num-bits */
#define BITARRAY_NUM_BITS_TO_BUF_SIZE(num_bits) \
    ((BITARRAY_NUM_BITS_TO_LIMBS(num_bits) + 1) * sizeof(bitarray))

/* fetch the limb containing bit position n */
#define BITARRAY_LIMB(bitarray, nbit) \
    ((bitarray)[1 + ((nbit) / BITARRAY_LIMB_BITS)])

/* build mask to select bit in limb */
#define BITARRAY_LIMBBIT(nbit) \
    ((1UL << ((nbit) % BITARRAY_LIMB_BITS)))

/*
 * To declare a bitarray with automatic storage:
 * {
 *     BITARRAY_DECLARE(x, 1024); // 'x' will now be set to bitarray
 * }
 */
#define BITARRAY_DECLARE(name, nbits) \
    bitarray (name)[1 + BITARRAY_NUM_BITS_TO_LIMBS((nbits))] = { nbits }

static inline size_t bitarray_num_limbs(bitarray *ba)
{
    return BITARRAY_NUM_BITS_TO_LIMBS(ba[0]);
}

static inline size_t bitarray_num_bits(bitarray *ba)
{
    return ba[0];
}

static inline void bitarray_set_bit(bitarray *ba, size_t n)
{
    BITARRAY_LIMB(ba, n) |= BITARRAY_LIMBBIT(n);
}

static inline void bitarray_clear_bit(bitarray *ba, size_t n)
{
    BITARRAY_LIMB(ba, n) &= ~BITARRAY_LIMBBIT(n);
}

static inline void bitarray_change_bit(bitarray *ba, size_t n)
{
    BITARRAY_LIMB(ba, n) ^= BITARRAY_LIMBBIT(n);
}

static inline int bitarray_test_bit(const bitarray *ba, size_t n)
{
    return !!(BITARRAY_LIMB(ba, n) & BITARRAY_LIMBBIT(n));
}

static inline void bitarray_zero(bitarray *ba)
{
    size_t nbytes = sizeof(bitarray) * bitarray_num_limbs(ba);
    memset(&ba[1], 0, nbytes);
}

/* clear bits at position 0 to (nbits-1) */
static inline void bitarray_clear_bits(bitarray *ba, size_t nbits)
{
    if (ba[0] >= nbits)
    {
        /* clear the entire bitarray */
        bitarray_zero(ba);
    }
    else
    {
        size_t nbytes;

        /*
         * cases:
         *   - (1) nbits align on byte boundary
         *   - (2) nbits does not align on byte boundary,
         *         manually clear remaining bits
         */
        if (nbits % CHAR_BIT == 0)
        {
            nbytes = nbits * CHAR_BIT;
        }
        else
        {
            size_t remaining_bits = nbits % CHAR_BIT;
            size_t i;

            /* clear bits in the partial byte first */
            for (i = nbits; i > (nbits - remaining_bits); i--)
            {
                bitarray_clear_bit(ba, i - 1);
            }
        }

        memset(&ba[1], 0, nbytes);
    }
}


/*
 * Allocation functions
 */
static inline bitarray *bitarray_alloc(size_t nbits)
{
        bitarray *ba = NULL;

        size_t nlimbs = 1 + BITARRAY_NUM_BITS_TO_LIMBS(nbits);

        ba = malloc(sizeof(bitarray) * nlimbs);
        if (ba)
        {
            ba[0] = nbits;
        }

        return ba;
}

static inline bitarray *bitarray_calloc(size_t nbits)
{
        bitarray *ba = NULL;

        size_t nlimbs = 1 + BITARRAY_NUM_BITS_TO_LIMBS(nbits);

        ba = calloc(sizeof(bitarray), nlimbs);
        if (ba)
        {
            ba[0] = nbits;
        }

        return ba;
}

static inline void bitarray_free(bitarray *ba)
{
    if (ba)
    {
        free(ba);
    }
}

/*
 * Take in a raw buffer and corresponding size and return a pointer to
 * a newly initialised bitarray struct.
 *
 * buf_size is required to be minimum 2*sizeof(bitarray) in size.
 *
 * e.g.
 *     unsigned char p[1024]; // bitarray will be slightly <8192 bits.
 *     bitarray *ba = bitarray_buf_init(p, sizeof(p));
 */
static inline bitarray *bitarray_buf_init(void *buf, size_t buf_size)
{
    bitarray *ba = buf;
    size_t nlimbs;
    size_t nbits;

    if (!ba)
    {
        return NULL;
    }

    /* the buf needs to have the size of at least 1 limb */
    if (buf_size < sizeof(bitarray))
    {
        return NULL;
    }

    /*
     * using the free available space (after allocating the initial limb)
     * to determine how many limbs are available.
     */
    nlimbs = (buf_size - sizeof(bitarray)) / sizeof(bitarray);

    if (nlimbs < 1)
    {
        nbits = 0;
    }
    else
    {
        nbits = nlimbs * sizeof(bitarray) * CHAR_BIT;
    }

    /* reserve a limb for storing number of bits */
    ba[0] = nbits;
    bitarray_zero(ba);

    return (ba);
}

static inline void bitarray_print_base16(bitarray *ba)
{
    bitarray i;
    size_t num_limbs = bitarray_num_limbs(ba);

    printf("DEBUG numbits=%lu\n", (unsigned long) ba[0]);
    printf("DEBUG sizeof(limb)=%lu\n", sizeof(ba[0]));
    printf("DEBUG num_limbs=%lu\n", num_limbs);
    for (i = 0; i <= num_limbs; i++)
    {
        unsigned char c;
        unsigned int j;
        size_t limb_size = sizeof(ba);

        for (j = 0; j < limb_size; j++)
        {
            /* mask the byte we want to print in hex */
            unsigned long mask = (0xFFUL) << (j * CHAR_BIT);
            c = (unsigned char) ((ba[i] & mask) >> (j * CHAR_BIT));
            printf("%02x", c);
        }

        printf(" ");
    }

    printf("\n");
}


/* ignore unused function warnings */
static void wno_unused_function_simple_bitarray_h(void)
{
    (void) bitarray_num_bits(NULL);
    (void) bitarray_change_bit(NULL, 0);
    (void) bitarray_clear_bit(NULL, 0);
    (void) bitarray_clear_bits(NULL, 0);
    (void) bitarray_alloc(0);
    (void) bitarray_calloc(0);
    (void) bitarray_free(NULL);
    return;
}

#endif