# uv 기반 자동화 스크립트

set -e  # 오류 발생 시 종료
VENV_DIR=".venv"

# 1. 가상환경 생성 (없을 경우)
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    uv venv "$VENV_DIR"
fi

# 2. 가상환경 활성화
echo "🚀 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# 3. 의존성 설치/업데이트
if [ -f "requirements.txt" ]; then
    echo "📂 Installing dependencies from requirements.txt..."
    uv pip install -r requirements.txt
    echo "⬆️  Upgrading packages..."
    # 전체 패키지 업그레이드는 직접 이름을 알아와야 하므로 아래와 같이 처리
    pkgs=$(uv pip freeze | cut -d'=' -f1)
    for pkg in $pkgs; do
        uv pip install --upgrade "$pkg"
    done
fi
if [ -f "pyproject.toml" ]; then
    echo "📂 Installing dependencies from pyproject.toml..."
    uv pip install .
fi

echo "✅ All done!"
