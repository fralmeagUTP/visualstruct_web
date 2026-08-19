#ifndef VISUALESTRUCT_HARNESS_COMMON_H
#define VISUALESTRUCT_HARNESS_COMMON_H

#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

static int harness_parse_int(const char *text, int *out) {
    char *end = NULL;
    long value;
    errno = 0;
    value = strtol(text, &end, 10);
    if (errno != 0 || end == text || *end != '\0' || value < INT_MIN || value > INT_MAX) {
        return 0;
    }
    *out = (int)value;
    return 1;
}

static int harness_error(const char *message) {
    fprintf(stderr, "harness-error: %s\n", message);
    return 2;
}

#endif
