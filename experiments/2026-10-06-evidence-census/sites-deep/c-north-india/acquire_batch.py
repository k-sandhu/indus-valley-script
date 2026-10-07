"""Fetch independent primary PDFs into the permitted local raw directory."""
from concurrent.futures import ThreadPoolExecutor
import json
from acquire_sources import acquire
URLS = {
 'bhagwanpura1993':'https://ignca.gov.in/Asi_data/80282.pdf',
 'mitathal1975':'https://ignca.gov.in/Asi_data/60032.pdf',
 'chandigarh_article':'https://ignca.gov.in/Asi_data/56352.pdf',
 'puratattva36':'https://ignca.gov.in/Asi_data/87942.pdf',
 'puratattva35':'https://ignca.gov.in/Asi_data/88233.pdf',
 'iar1976':'https://www.asiaurangabadcircle.com/assets/files/publications/1976-1977.pdf',
 'iar1987':'https://assets.ctfassets.net/l47hkrce4wip/CPdkhXlLJ48xGlpSkhTlf/9e60cdb7feb376ab09962fd5f9f080c8/009_Indian_Archaeology_A_Review_1987-88.pdf',
 'iar2008':'https://nmma.nic.in/nmma/NAS1/nmma_doc/IAR/Indian%20Archaeology%20%202008%20-%202009%20%20A%20Review.pdf',
 'iar2011':'https://nmma.nic.in/nmma/NAS1/nmma_doc/IAR/Indian%20Archaeology%20%202011%20-%202012%20%20A%20Review.pdf',
 'iar2013':'https://nmma.nic.in/nmma/NAS1/nmma_doc/IAR/Indian%20Archaeology%20%202013%20-%202014%20%20A%20Review.pdf',
 'tn2025':'https://www.tnarch.gov.in/sites/default/files/IVC_PROCEEDINGS_RMRL.pdf',
 'konasukawa':'https://easaa.org/wp-content/uploads/2023/01/Ayumu-Konasukawa-9.pdf',
 'masudpur2021':'https://www.vkm.ac.in/uploads/academics/staff/book%26paper/artic/paper.pdf',
 'iar1999':'https://www.asiaurangabadcircle.com/assets/files/publications/1999-2000.pdf',
 'rakhigarhi_inventory':'https://ignca.gov.in/Asi_data/84884.pdf',
 'iar2009':'https://nmma.nic.in/nmma/NAS1/nmma_doc/IAR/Indian%20Archaeology%20%202009%20-%202010%20%20A%20Review.pdf',
 'iar1985':'https://nmma.nic.in/nmma/NAS1/nmma_doc/IAR/Indian%20Archaeology%201985-86%20A%20Review.pdf',
 'kotla1929':'https://ir.nbu.ac.in/bitstreams/c173363c-2f0f-4fef-aaf9-baeff0e46af2/download',
}
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=5) as pool:
  for row in pool.map(lambda x:acquire(x[0],x[1]),URLS.items()): print(json.dumps(row,ensure_ascii=True),flush=True)
