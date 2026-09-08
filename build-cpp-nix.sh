#!/run/current-system/sw/bin/bash
set -euo pipefail

DEST_DIR="$(pwd)/dist"
mkdir -p "$DEST_DIR"

echo "==> Building portable Krita C++ plugin via Nix..."
nix build .#portable-plugin --out-link result-plugin

echo "==> Copying output files to: $DEST_DIR"
# Copy direct files for easy grabbing
cp result-plugin/lib/kritaplugins/kritashapesselection.so "$DEST_DIR/kritashapesselection.so"
cp result-plugin/share/krita/actions/kritashapesselection.action "$DEST_DIR/kritashapesselection.action"

# Copy structure matching Krita installation hierarchy
mkdir -p "$DEST_DIR/lib/kritaplugins" "$DEST_DIR/share/krita/actions"
cp result-plugin/lib/kritaplugins/kritashapesselection.so "$DEST_DIR/lib/kritaplugins/"
cp result-plugin/share/krita/actions/kritashapesselection.action "$DEST_DIR/share/krita/actions/"

# Copy ready-to-share zip
if [ -f "result-plugin/dist/uv-select-linux.zip" ]; then
    cp result-plugin/dist/uv-select-linux.zip "$DEST_DIR/uv-select-linux.zip"
    cp result-plugin/dist/uv-select-linux.zip "$(pwd)/uv-select-linux.zip"
fi

echo ""
echo "==> Done! You can grab your files directly from:"
echo "    - $DEST_DIR/kritashapesselection.so"
echo "    - $DEST_DIR/kritashapesselection.action"
echo "    - $DEST_DIR/uv-select-linux.zip"
echo ""
