## Installation    

cd </path/to/socmigration>  
conda env create -f environment.yaml

## Parsing Instagram example
python inst_parser.py  
--working_login=vova.putin  
--working_password=putin777  
--parsed_user=djoe.biden

## Posting on VK example
python vk_poster  
--data_dir=./out  
--start_date="22/08/2021 12:00"  
--user_login=vova.putin  
--user_password=putin777
