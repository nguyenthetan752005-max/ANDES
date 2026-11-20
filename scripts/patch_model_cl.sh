#!/bin/bash
# Vá Help/model.cl để chạy trên SBCL >= 2.x
# (SBCL mới export SB-EXT:CREATE -> xung đột với ANDES-DATABASE:CREATE)
#
# Dùng:  bash patch_model_cl.sh [đường_dẫn_model.cl]
set -e
f="${1:-$HOME/andes-stable/Help/model.cl}"

if grep -q 'shadowing-import (find-symbol "CREATE"' "$f"; then
    echo "Đã vá rồi: $f"
    exit 0
fi

sed -i 's#^\([[:space:]]*\)(use-package :andes-database))#\1(shadowing-import (find-symbol "CREATE" :andes-database))\n\1(use-package :andes-database))#' "$f"
echo "Đã vá: $f"
