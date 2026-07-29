from database import execute_query

sql = "UPDATE usuarios SET password_hash = '200001' WHERE username = '200001' AND (password_hash IS NULL OR password_hash = '')"
execute_query(sql, commit=True)
print("User 200001 password updated successfully!")
