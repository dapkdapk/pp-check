pip list | awk '{print $1}' | grep pp-check | xargs pip uninstall -y
rm -fr ./dist
poetry install
poetry run build

echo "----------------------------------------------------"
echo Copy string below and paste into e.g. ~/.bash_profile
echo "----------------------------------------------------"
mkdir bin
cp dist/ppcheck bin
cat << EOF

export PATH="\$PATH:$(pwd)/bin"

EOF
echo "----------------------------------------------------"
