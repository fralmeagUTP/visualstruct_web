# Publication packaging reopen only

Operation audit.publish-main-canonical. Exact reason: CI Linux sanitizer shell failed before compilation from canonical CRLF packaging; correct only shell transport line endings to LF, no algorithms/canonical D code changes.

Evidence new: CI-C17-failed.log from37544589568 atSHA62d7bde. User authorization to main publication covers necessary transport correction, not algorithm changes or closed audit repetition. Only isolated scripts/check_c_sanitizers_linux.sh EOL packaging correction; preserve failing commit/log and noVPS/SDD.
