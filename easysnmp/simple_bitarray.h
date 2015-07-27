#ifndef SIMPLE_BITARRAY_H
#define SIMPLE_BITARRAY_H

#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <string.h>

#if (__STDC_VERSION__ < 199901L)
#define inline
#endif

typedef unsigned int bitarray_word;

/*
 * this is not guaranteed to be portable since an integral type size
 * doesn't necessarily define the range
 */
#define BITARRAY_LIMB_BITS (sizeof(bitarray_word) * CHAR_BIT)

/* macro to find the number of limbs to store num-bits */
#define BITARRAY_NUM_BITS_TO_LIMBS(num_bits) \
    (((num_bits) + BITARRAY_LIMB_BITS - 1) / BITARRAY_LIMB_BITS)

/* fetch the limb containing bit position n */
#define BITARRAY_LIMB(bitarray, n_bit) \
    ((bitarray)[1 + ((n_bit) / BITARRAY_LIMB_BITS)].limb)

/* build mask to select bit in limb */
#define BITARRAY_LIMBBIT(n_bit) \
    ((1UL << ((n_bit) % BITARRAY_LIMB_BITS)))

/*
 * we use a struct to give a name;
 * when used, we reserve bitarray[0] for storing the number of bits.
 */
typedef struct
{
    bitarray_word limb;
} bitarray;

/*
 * To declare a bitarray with automatic storage:
 * {
 *     BITARRAY_DECLARE(x, 1024); // 'x' will now be set to bitarray
 * }
 */
#define BITARRAY_DECLARE(name, nbits) \
    bitarray (name)[1 + BITARRAY_NUM_BITS_TO_LIMBS((nbits))] = { { nbits } }

static inline size_t bitarray_num_limbs(bitarray *bitarray)
{
    return BITARRAY_NUM_BITS_TO_LIMBS(bitarray[0].limb);
}

static inline size_t bitarray_num_bits(bitarray *bitarray)
{
    return bitarray[0].limb;
}

static inline void bitarray_set_bit(bitarray *bitarray, bitarray_word n)
{
    BITARRAY_LIMB(bitarray, n) |= BITARRAY_LIMBBIT(n);
}

static inline void bitarray_clear_bit(bitarray *bitarray, bitarray_word n)
{
    BITARRAY_LIMB(bitarray, n) &= ~BITARRAY_LIMBBIT(n);
}

static inline void bitarray_change_bit(bitarray *bitarray, bitarray_word n)
{
    BITARRAY_LIMB(bitarray, n) ^= BITARRAY_LIMBBIT(n);
}

static inline int bitarray_test_bit(const bitarray *bitarray, bitarray_word n)
{
    return !!(BITARRAY_LIMB(bitarray, n) & BITARRAY_LIMBBIT(n));
}

static inline void bitarray_zero(bitarray *bitarray)
{
    memset(&bitarray[1], 0, bitarray_num_limbs(bitarray));
}

/*
 * Allocation functions
 */
static inline bitarray *bitarray_alloc(unsigned long nbits)
{
        bitarray *ba = NULL;

        size_t n_limbs = 1 + BITARRAY_NUM_BITS_TO_LIMBS(nbits);

	ba = malloc(sizeof(bitarray) * n_limbs);
        if (ba)
        {
            ba[0].limb = nbits;
        }

        return ba;
}

static inline bitarray *bitarray_calloc(unsigned long nbits)
{
        bitarray *ba = NULL;

        size_t n_limbs = 1 + BITARRAY_NUM_BITS_TO_LIMBS(nbits);

	ba = calloc(sizeof(bitarray), n_limbs);
        if (ba)
        {
            ba[0].limb = nbits;
        }

	return ba;
}

static inline void bitarray_free(bitarray *bitarray)
{
    if (bitarray)
    {
        free(bitarray);
    }
}

static inline void bitarray_buf_init(void *buf, size_t buf_size)
{
        bitarray *ba = buf;

        size_t nbits = (buf_size - sizeof(bitarray_word)) * CHAR_BIT;

        ba[0].limb = nbits;
}

static inline void bitarray_print_base16(bitarray *bitarray)
{
    bitarray_word i;
    size_t num_limbs = bitarray_num_limbs(bitarray);

    printf("sizeof(limb)=%lu\n", sizeof(bitarray[0].limb));
    printf("num_limbs=%lu\n", num_limbs);
    for (i = 0; i <= num_limbs; i++)
    {
            unsigned char c;
            unsigned int j;
            size_t limb_size = sizeof(bitarray_word);

            for (j = 0; j < limb_size; j++)
            {
                /* mask the byte we want to print in hex */
                unsigned long mask = (0xFFUL) << (j * CHAR_BIT);
                c = (unsigned char) ((bitarray[i].limb & mask) >> (j * CHAR_BIT));
                printf("%02x", c);
            }

            printf(" ");
        }

    printf("\n");
}


#endif
