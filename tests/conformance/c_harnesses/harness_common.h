#ifndef VISUALESTRUCT_HARNESS_COMMON_H
#define VISUALESTRUCT_HARNESS_COMMON_H

#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define HARNESS_QA_SCHEMA "didactic-c-event/v1"
#define HARNESS_QA_OPERATION(name, phase) harness_qa_emit("operation", (phase), (name))
#define HARNESS_QA_CONDITION(detail) harness_qa_emit("condition", "output", (detail))
#define HARNESS_QA_RETURN(detail) harness_qa_emit("return", "output", (detail))
#define HARNESS_QA_RETURN_INT(label, value) do { \
    char harness_qa_return_detail[128]; \
    (void)snprintf(harness_qa_return_detail, sizeof(harness_qa_return_detail), \
                   "%s=%d", (label), (value)); \
    harness_qa_emit("return", "output", harness_qa_return_detail); \
} while (0)
#define HARNESS_QA_POINTER(detail) harness_qa_emit("pointer_link", "after", (detail))
#define HARNESS_QA_FREE(detail) harness_qa_emit("free", "after", (detail))
#define HARNESS_QA_BRANCH(detail) harness_qa_emit("branch", "output", (detail))
#define HARNESS_QA_CALL(detail, phase) harness_qa_emit("call", (phase), (detail))
#define HARNESS_QA_ALLOCATION(detail) harness_qa_emit("allocation", "after", (detail))
#define HARNESS_QA_COMPARISON(detail) harness_qa_emit("comparison", "output", (detail))
#define HARNESS_QA_SNAPSHOT(detail) harness_qa_emit("snapshot", "before", (detail))

static const char *harness_qa_structure_id = "unknown";
static unsigned long harness_qa_sequence = 0UL;

static int harness_qa_enabled(void) {
    const char *value = getenv("VISUALESTRUCT_QA_EVENTS");
    return value != NULL && strcmp(value, "1") == 0;
}

static void harness_qa_json_string(FILE *stream, const char *text) {
    const unsigned char *cursor = (const unsigned char *)text;
    fputc('"', stream);
    while (*cursor != '\0') {
        if (*cursor == '"' || *cursor == '\\') {
            fputc('\\', stream);
            fputc((int)*cursor, stream);
        } else if (*cursor == '\n') {
            fputs("\\n", stream);
        } else if (*cursor == '\r') {
            fputs("\\r", stream);
        } else if (*cursor == '\t') {
            fputs("\\t", stream);
        } else if (*cursor >= 0x20U) {
            fputc((int)*cursor, stream);
        }
        cursor++;
    }
    fputc('"', stream);
}

static void harness_qa_emit(const char *event, const char *phase, const char *detail) {
    if (!harness_qa_enabled()) return;
    fprintf(stderr, "{\"schema\":\"%s\",\"sequence\":%lu,\"structure_id\":",
            HARNESS_QA_SCHEMA, harness_qa_sequence++);
    harness_qa_json_string(stderr, harness_qa_structure_id);
    fputs(",\"event\":", stderr); harness_qa_json_string(stderr, event);
    fputs(",\"phase\":", stderr); harness_qa_json_string(stderr, phase);
    fputs(",\"detail\":", stderr); harness_qa_json_string(stderr, detail == NULL ? "" : detail);
    fputs("}\n", stderr);
}

static void harness_qa_begin(const char *structure_id, int argc, char **argv) {
    int index;
    harness_qa_structure_id = structure_id;
    harness_qa_sequence = 0UL;
    harness_qa_emit("lifecycle", "begin", "harness invocation");
    if (!harness_qa_enabled()) return;
    for (index = 1; index < argc; index++) {
        harness_qa_emit("argument", "input", argv[index]);
    }
}

static void harness_qa_end(void) {
    harness_qa_emit("lifecycle", "end", "canonical state emitted");
}

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
    harness_qa_emit("error", "return", message);
    fprintf(stderr, "harness-error: %s\n", message);
    return 2;
}

#endif
