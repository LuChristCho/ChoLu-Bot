import pandas as pd
from pathlib import Path
import json
from typing import Dict, List, Any

class Database:
    def __init__(self):
        self.db_path = Path(__file__).parent / "data/db.csv" 
        self.config_path = Path(__file__).parent / "src/config.json"
        self.df = self._load_database()
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        with open(self.config_path) as f:
            return json.load(f)

    def _load_database(self) -> pd.DataFrame:
        if self.db_path.exists():
            df = pd.read_csv(self.db_path)
            int_columns = ['UserID', 'Ban', 'Adminstration', 'Reminder']
            df[int_columns] = df[int_columns].astype(int)
            return df
        else:
            return pd.DataFrame(columns=[
                'UserID', 'Ban', 'Adminstration', 
                'API', 'Reminder', 'Name'
            ])

    def save_database(self):
        self.df.to_csv(self.db_path, index=False)

    def get_config(self) -> Dict[str, Any]:
        return {
            'BOT_TOKEN': self.config['BOT_TOKEN'],
            'OWNER_ID': int(self.config['OWNER_ID']),
            'LOG_USER_ID': int(self.config['LOG_USER_ID']),
            'TIMEZONE': self.config['TIMEZONE']
        }

    def get_dynamic_data(self) -> Dict[str, Any]:
        return {
            'COINMARKETCAP_API_KEYS': dict(zip(
                self.df['UserID'].astype(str),
                self.df['API']
            )),
            'USER_LIST': self.df['UserID'].tolist(),
            'ADMIN_LIST': self.df[self.df['Adminstration'] == 1]['UserID'].tolist(),
            'BANNED_USERS': self.df[self.df['Ban'] == 1]['UserID'].tolist(),
            'FOOD_RESERVATION_LIST': self.df[self.df['Reminder'] == 1]['UserID'].tolist()
        }

    def update_dataframe(self, 
                        user_list: List[int],
                        admin_list: List[int],
                        banned_users: List[int],
                        reminder_list: List[int],
                        cmc_api_keys: Dict[str, str]):
        existing_users = set(self.df['UserID'])
        new_users = set(user_list) - existing_users
        
        if new_users:
            new_rows = []
            for user_id in new_users:
                new_rows.append({
                    'UserID': user_id,
                    'Ban': 0,
                    'Adminstration': 0,
                    'API': "",
                    'Reminder': 0,
                    'Name': f"User_{user_id}" 
                })
            
            self.df = pd.concat([self.df, pd.DataFrame(new_rows)], ignore_index=True)
        
        self.df['Adminstration'] = self.df['UserID'].isin(admin_list).astype(int)
        self.df['Ban'] = self.df['UserID'].isin(banned_users).astype(int)
        self.df['Reminder'] = self.df['UserID'].isin(reminder_list).astype(int)
        self.df['API'] = ""
        
        for user_id_str, api_key in cmc_api_keys.items():
            user_id = int(user_id_str)
            if user_id in self.df['UserID'].values:
                self.df.loc[self.df['UserID'] == user_id, 'API'] = api_key
        
        self.save_database()

    def export_database(self, bot, chat_id: int,
                      user_list: List[int],
                      admin_list: List[int],
                      banned_users: List[int],
                      reminder_list: List[int],
                      cmc_api_keys: Dict[str, str]) -> bool:
        try:
            self.update_dataframe(
                user_list=user_list,
                admin_list=admin_list,
                banned_users=banned_users,
                reminder_list=reminder_list,
                cmc_api_keys=cmc_api_keys
            )
            
            temp_path = Path(__file__).parent / "temp_db.csv"
            self.df.to_csv(temp_path, index=False, encoding='utf-8-sig')
            
            with open(temp_path, 'rb') as doc:
                bot.send_document(
                    chat_id=chat_id,
                    document=doc,
                    caption="📊 Database Export"
                )
            
            temp_path.unlink()
            return True
        except Exception as e:
            print(f"Error exporting database: {e}")
            return False

# Create a single instance of the database
db = Database()