# uv format 자동화 스크립트

set -e  # 오류 발생 시 즉시 종료

echo "🔍 Checking Python formatting with uv..."
if uv format --check .; then
    echo "✅ All files are already formatted!"
else
    echo "✏️ Formatting files..."
    uv format .
    echo "✅ Formatting complete."
fi