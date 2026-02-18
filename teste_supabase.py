from utils.supabase_client import get_client

sb = get_client()

resp = sb.table("torres_view").select("*").limit(2).execute()

print(resp.data)