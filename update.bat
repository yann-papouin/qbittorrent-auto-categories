REM Set codepage to UTF-8
chcp 65001 > nul

call .venv/Scripts/activate.bat

python generate_categories.py ^
    --base-path=E:\Animations ^
    --cleanlist-path=user_clean_list.py ^
    --ignorelist-path=user_ignore_list.py ^
    --remove-dir ^
    --use-subcategories
    
python generate_categories.py ^
    --base-path=E:\Emissions ^
    --cleanlist-path=user_clean_list.py ^
    --ignorelist-path=user_ignore_list.py ^
    --remove-dir ^
    --use-subcategories
    
python generate_categories.py ^
    --base-path=E:\Films ^
    --cleanlist-path=user_clean_list.py ^
    --ignorelist-path=user_ignore_list.py ^
    --remove-dir ^
    --use-subcategories

python generate_categories.py ^
    --base-path=E:\Séries ^
    --cleanlist-path=user_clean_list.py ^
    --ignorelist-path=user_ignore_list.py ^
    --remove-dir ^
    --use-subcategories
    
python generate_categories.py ^
    --base-path=E:\Spectacles ^
    --cleanlist-path=user_clean_list.py ^
    --ignorelist-path=user_ignore_list.py ^
    --remove-dir ^
    --use-subcategories

