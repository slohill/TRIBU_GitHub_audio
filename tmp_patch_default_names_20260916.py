from pathlib import Path
names="['Valkor','Xodia','Oldirn','Mundris','Ferna','Dronk','Spoltreg','Nimun','Raenura','Keplet']"
for fn in ['index.html','server/server.js']:
 p=Path(fn); s=p.read_text(encoding='utf-8')
 if fn=='index.html':
  old="const ONLINE_RANDOM_NAMES=['Aube-Rousse','Corne-de-Brume','Loup-Serein','Éclat-de-Silex','Rivière-Noire','Chêne-Ardent','Renard-d’Or','Lune-Fauve','Vent-du-Nord','Pierre-Claire'];"
  new='const ONLINE_RANDOM_NAMES='+names+';'
 else:
  old="const DEFAULT_NAMES = ['Aube','Brume','Croc','Dune','Écorce','Faucon','Givre','Lune','Silex','Torrent'];"
  new='const DEFAULT_NAMES = '+names+';'
 assert old in s, (fn,'old names not found')
 s=s.replace(old,new,1)
 p.write_text(s,encoding='utf-8')
