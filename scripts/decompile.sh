#!/bin/sh

export DofusInvoker="C:/Users/Totos/AppData/Local/Ankama/Dofus/DofusInvoker.swf"
export selectclass='com.ankamagames.dofus.BuildInfos,com.ankamagames.dofus.network.++,com.ankamagames.jerakine.network.++'
export config='parallelSpeedUp=0'

cd "$( dirname "${BASH_SOURCE[0]}" )"
cd ..
if [  -d "./sources" ]; then
	rm -r "./sources";
fi
C:/Users/Totos/Programs/Flash_Decompiler/ffdec.sh -config "$config" -selectclass "$selectclass" -export script ./sources $DofusInvoker