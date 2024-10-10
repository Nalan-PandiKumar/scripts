#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define ZERO 0x30 // ASCII for '0'
#define ONE 0x31  // ASCII for '1'

#define BYTE 0x8   // Defines 8 bits in a byte
#define SPACE 0x20 // ASCII for ' ' (space)

// Function to check if the given string is a valid binary number
bool check_isvalid_binary(char *binary_num)
{
    /*
        Iterates over each character in the input string `binary_num`,
        checks if each character is either '0' or '1'.
        Returns false if any character is invalid, otherwise returns true.
    */
    for (size_t i = 0; i < strlen(binary_num); i++)
    {
        char bit = *(binary_num + i);
        if (bit != ONE && bit != ZERO)
            return false; // Invalid binary digit found
    }
    return true; // All characters are valid binary digits
}

// Function to calculate the number of spaces needed between bytes
size_t calculate_space(size_t padded_length)
{
    /*
        Takes the padded length of the binary string as input and calculates
        the number of spaces required to separate bytes (every 8 bits).
    */
    return (padded_length / 2) - 1; // One space between each byte
}

// Function to calculate the number of padding bits required for byte alignment
size_t padd_bytes(char *binary_num)
{
    /*
        Calculates how many padding bits (if any) are needed to make
        the length of the binary number a multiple of 8 (1 byte).
    */
    size_t length = strlen(binary_num);
    return (BYTE - (length % BYTE)) % BYTE; // Returns number of padding bits
}

// Function to calculate the total size of the binary number in bits
size_t size_of_bits(char *binary_num)
{
    /*
        Calculates the total size of the binary number in bits after adding
        any necessary padding to align the binary number to the nearest byte.
    */
    return strlen(binary_num) + padd_bytes(binary_num);
}

// Function to format the binary string with padding and spaces
char *format_binary(char *binary_num)
{
    /*
        Formats the given binary string by adding necessary zero-padding
        to make the length a multiple of 8 bits (byte-aligned) and inserts
        spaces between each byte for readability.
    */

    // Calculate the total bit length (original length + padding)
    size_t bit_length = size_of_bits(binary_num);

    // Calculate how many padding bits are needed
    size_t padd_length = padd_bytes(binary_num);

    // Calculate how many spaces are needed between bytes
    size_t space_length = calculate_space(bit_length);

    // Allocate memory on the heap for the formatted string (including padding, spaces, and '\0')
    char *heap_chunk = (char *)malloc(bit_length + space_length + 1);

    // Check if memory allocation succeeded
    if (heap_chunk == NULL)
        return NULL; // Allocation failed, return NULL

    // Add zero-padding to make the total length byte-aligned
    size_t i = 0;
    for (; i < padd_length; i++)
    {
        *(heap_chunk + i) = ZERO; // Add '0' to the beginning
    }

    // Insert binary digits into the formatted string, adding spaces between bytes
    size_t space_flag = BYTE; // Insert a space after every byte (8 bits)
    while (*binary_num)
    {
        if (i % space_flag == 0 && i != 0)
        {
            *(heap_chunk + i) = SPACE; // Insert a space between bytes
            i++;
            space_flag += (BYTE + 1); // Adjust space position for next byte
        }
        *(heap_chunk + i) = *binary_num; // Copy binary digits to the formatted string
        binary_num++;
        i++;
    }

    *(heap_chunk + i) = '\0'; // Null-terminate the string
    return heap_chunk;        // Return the formatted binary string
}

int main(int argc, char **argv)
{
    // Check if a binary string is passed as a command-line argument
    if (argc > 1)
    {
        // Get the binary number from the arguments
        char *binary_num = *(argv + 1);

        // Check if the binary string is valid
        if (check_isvalid_binary(binary_num))
        {
            // Format the binary string to align bytes and insert spaces
            char *formatted_binary = format_binary(binary_num);

            // Calculate the size in bytes (total bits / 8)
            size_t size = size_of_bits(binary_num) / BYTE;

            // If formatting succeeded, print the formatted binary and its size
            if (formatted_binary != NULL)
            {
                printf("0b:\x1b[0;32m%s\x1b[0m | size:\x1b[0;31m%zu-%s\x1b[0m\n",
                       formatted_binary, size, (size > 1) ? "Bytes" : "Byte");
                free(formatted_binary); // Free allocated memory
            }
            else
            {
                // Memory allocation failed
                printf("\x1b[0;31m The program can't find a free memory\x1b[0m\n");
                return -1; // Exit with an error code
            }
        }
        else
        {
            // Input string is not a valid binary number
            printf("\x1b[0;31m <ERROR> :Invalid Binary\x1b[0m\n");
            return -1; // Exit with an error code
        }
    }
    else
    {
        // No command-line argument passed
        printf("\x1b[0;31m <ERROR> :The process expects command line arguments\x1b[0m\n");
        return -1; // Exit with an error code
    }

    return 0; // Successful execution
}
