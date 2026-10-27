import tempfile,unittest
from app import create_app
from app.config import Config
from app.domain.hash.educational_capacity import MAX_VISUAL_CAPACITY
class HashHelp(unittest.TestCase):
 def test_actual_page_limits_and_history(self):
  with tempfile.TemporaryDirectory() as folder:
   class T(Config):TESTING=True;SESSION_CACHE_DIR=folder
   r=create_app(T).test_client().get('/help/hash/hash_table');self.assertEqual(r.status_code,200);s=r.get_data(as_text=True)
   self.assertIn(f'entre 1 y {MAX_VISUAL_CAPACITY} buckets',s);self.assertIn('INT_MAX limita el tipo',s);self.assertIn('no se truncan',s);self.assertIn('historial y main.c',s)
if __name__=='__main__':unittest.main()
