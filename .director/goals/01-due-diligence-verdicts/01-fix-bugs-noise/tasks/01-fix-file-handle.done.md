# Task: Fix unclosed file handle in vision converter

## What To Do

Find and fix the unclosed image file handle in the vision converter module. The file should be properly closed after reading, using a context manager (`with` statement) to ensure cleanup even if an error occurs.

## Why It Matters

An unclosed file handle can cause resource leaks during batch processing of scanned documents, potentially hitting OS file descriptor limits on large opportunity folders with many images.

## Size

**Estimate:** small

Single file fix -- find the open() call without a corresponding close or context manager, and wrap it properly.

## Done When

- [x] The image file handle in the vision converter uses a context manager
- [x] Existing converter tests still pass
- [x] No other unclosed file handles in the converter module

## Needs First

Nothing -- this can start right away.
