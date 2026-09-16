from pathlib import Path
p=Path('index.html'); s=p.read_text(encoding='utf-8')
start=s.index('const CARD_ZOOM_RULES=')
end=s.index('function openOfficialCard',start)
block=s[start:end]
repls={
'"Canicule":"Lorsque Canicule est activée, les régions enneigées deviennent tempérées et les régions tempérées deviennent désertiques ; les régions naturellement désertiques restent désertiques. Les terrains verrouillés des Cités conservent leur type. L’effet persiste jusqu’au prochain changement ou à la fin prévue de l’effet climatique."':'"Canicule":"Les Régions tempérées deviennent désertiques et les Régions enneigées deviennent tempérées tant que Canicule est active"',
'"Vague de froid":"Lorsque Vague de froid est activée, les régions tempérées deviennent enneigées et les régions désertiques deviennent tempérées ; les régions naturellement enneigées restent enneigées. Les terrains verrouillés des Cités conservent leur type. L’effet persiste jusqu’au prochain changement ou à la fin prévue de l’effet climatique."':'"Vague de froid":"Les Régions tempérées deviennent enneigées et les Régions désertiques deviennent tempérées tant que Vague de froid est active"',
'"Givre mortel":"Les Griffes-Blanches sont immunisés. Les unités non immunisées présentes en Mer de glace sont détruites. Ensuite, chaque joueur non immunisé doit sacrifier la moitié, arrondie au supérieur, de ses régions enneigées éligibles. Icenia est protégée."':'"Givre mortel":"Chaque joueur.euse non Griffe-Blanche sacrifie la moitié (arrondie au supérieur) de ses Régions enneigées"',
'"Tempête de sable":"Les Reptones sont immunisés. Chaque joueur non immunisé doit sacrifier la moitié, arrondie au supérieur, de ses régions désertiques éligibles. Sundo est protégée. Tempête de sable ne détruit rien en Mer de feu."':'"Tempête de sable":"Chaque joueur.euse non Reptone sacrifie la moitié (arrondie au supérieur) de ses Régions désertiques"',
'"Tempête en mer":"Pendant l’effet de Tempête en mer, tout déplacement impliquant une mer est soumis à un jet : résultat pair, le déplacement réussit ; résultat impair, les unités engagées sont perdues et la destination ratée est verrouillée pour le reste du tour."':'"Tempête en mer":"Tant que Tempête en mer est activée, pour chaque déplacement d’une ou vers une Aire maritime, lancez un dé, si le résultat est impaire les unités sont détruites."',
'"En quête de destruction":"Lorsque cet Oracle est activé, le Dragon doit parcourir 5 cases différentes. Le joueur qui a activé l’Oracle choisit successivement ses déplacements ; les bots effectuent ces choix automatiquement. Tant que cet Oracle est visible et actif, les résultats prévus par sa règle peuvent également déclencher la destruction du Dragon."':'"En quête de destruction":"Déplacez le dragon de 5 cases différentes ; Tant que En quête de destruction est active, chaque fois que vous faites 4 ou 5 durant la phase Oracle cela active aussi le dragon."'
}
for old,new in repls.items(): assert old in block, old[:50]; block=block.replace(old,new,1)
s=s[:start]+block+s[end:]
start=s.index('function oracleEffectText(name){'); end=s.index('function showOracleNotice',start)
new='''function oracleEffectText(name){
 if(name==='Canicule')return 'Les Régions tempérées deviennent désertiques et les Régions enneigées deviennent tempérées tant que Canicule est active<br><br><i>La végétation se raréfie, l’eau vient à manquer, les sols s\'assèchent et les vents soulèvent des poussières depuis lesquelles certaines créatures à sang froid peuvent surgir…</i>';
 if(name==='Vague de froid')return 'Les Régions tempérées deviennent enneigées et les Régions désertiques deviennent tempérées tant que Vague de froid est active<br><br><i>Sous un lourd manteau blanc les paysages et les cultures disparaissent. Durant la longue nuit, gare aux lames nordiques aussi froides que le givre.</i>';
 if(name==='Givre mortel')return 'Chaque joueur.euse non Griffe-Blanche sacrifie la moitié (arrondie au supérieur) de ses Régions enneigées<br><br><i>Le vent cesse de souffler, les crépitements chantent par delà les forêts et les montagnes, le temps se fige et les vivants avec lui…</i>';
 if(name==='Tempête de sable')return 'Chaque joueur.euse non Reptone sacrifie la moitié (arrondie au supérieur) de ses Régions désertiques<br><br><i>Des murs de sable viennent asphyxier et ensevelir les populations des contrées arides.</i>';
 if(name==='Tempête en mer')return 'Tant que Tempête en mer est activée, pour chaque déplacement d’une ou vers une Aire maritime, lancez un dé, si le résultat est impaire les unités sont détruites.';
 if(name==='En quête de destruction')return 'Déplacez le dragon de 5 cases différentes ; Tant que En quête de destruction est active, chaque fois que vous faites 4 ou 5 durant la phase Oracle cela active aussi le dragon.<br><br><i>Il est le feu, il est la mort…</i>';
 return '';
}
function oracleNoticeTitle(name){
 if(name==='Canicule')return 'Canicule activée';
 if(name==='Vague de froid')return 'Vague de froid activée';
 if(name==='Tempête de sable')return 'Tempêtes de sables activée';
 if(name==='Givre mortel')return 'Givre mortel activé';
 if(name==='Tempête en mer')return 'Tempête en mer activée';
 if(name==='En quête de destruction')return 'En quête de destruction activée';
 return name+' activé';
}
'''
s=s[:start]+new+s[end:]
s=s.replace("$('oracleNoticeTitle').textContent='ORACLE ACTIVÉ — '+name.toUpperCase();\n $('oracleNoticeText').textContent=oracleEffectText(name);","$('oracleNoticeTitle').textContent=oracleNoticeTitle(name);\n $('oracleNoticeText').innerHTML=oracleEffectText(name);",1)
s=s.replace("$('oracleNoticeTitle').textContent='ORACLE ACTIVÉ — '+name.toUpperCase();\n $('oracleNoticeText').textContent=oracleEffectText(name);","$('oracleNoticeTitle').textContent=oracleNoticeTitle(name);\n $('oracleNoticeText').innerHTML=oracleEffectText(name);",1)
p.write_text(s,encoding='utf-8')
