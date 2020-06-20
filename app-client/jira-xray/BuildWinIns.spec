# -*- mode: python -*-

block_cipher = None

datas = [ 
            ( './Resources/releasenotes.txt', '.'),
            ( './Resources/plugin.png', '.'),
            ( './Files', 'Files' ),
            ( './HISTORY', '.'),
            ( './config.json', '.'),
            ( './LICENSE-LGPLv21', '.'),
            ( './Dlls64/opengl32sw.dll', '.' ),
            ( './Dlls64/libeay32.dll', '.' ),
            ( './Dlls64/ssleay32.dll', '.' ),
            ( './Dlls64/imageformats', 'imageformats' ),
            ( './Files', 'Files' ),
            ( './Resources/plugin.ico', '.' ),
        ]
             
a = Analysis(['MyPlugin.py'],
             pathex=[ '.', './Dlls64/' ],
             binaries=[],
             datas=datas,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='JiraXRayPlugin',
          debug=0,
          strip=0,
          upx=1,
          console=0,
          icon='./Resources/plugin.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=0,
               upx=1,
               name='JiraXRayPlugin')