#!/usr/bin/env bash

for fig_file in fig_*.py; do
    python3 "$fig_file"
done

if [ -n $( command -v "gs" ) ]; then
    # if ghostscript is installed, convert fonts to paths in PDF files
    find figs/ -maxdepth 1 -name "*.pdf" \
        -exec gs -q -o {}.opt -dNoOutputFonts -sPAPERSIZE=a4 -sDEVICE=pdfwrite {} \; \
        -exec mv {}.opt {} \;
fi
