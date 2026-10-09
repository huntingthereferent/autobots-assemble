from arc_agi import Arcade,OperationMode
e=Arcade(operation_mode=OperationMode.NORMAL).make('ft09')
for i,lev in enumerate(e._game._levels):
 print('LEVEL',i+1,'COLORS',lev.get_data('cwU'),'COUNTER',lev.get_data('kCv'),'Hkx',len(lev.get_sprites_by_tag('Hkx')),'NTi',len(lev.get_sprites_by_tag('NTi')),'BS',len(lev.get_sprites_by_tag('bsT')),'PATTERN',lev.get_data('elp'),flush=True)
