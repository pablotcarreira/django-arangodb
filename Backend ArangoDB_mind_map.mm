<map version="1.0.1">
<!-- To view this file, download free mind mapping software FreeMind from http://freemind.sourceforge.net -->
<attribute_registry>
<attribute_name NAME="time" VISIBLE="true"/>
</attribute_registry>
<node CREATED="1476102715170" ID="ID_88224143" MODIFIED="1476110079440" TEXT="Utilizar o ArangoDB com o Django">
<node CREATED="1476103568184" HGAP="10" ID="ID_1643999461" MODIFIED="1476110078100" POSITION="right" TEXT="Backend Para ArangoDB" VSHIFT="-77">
<node CREATED="1476103597146" ID="ID_155132062" MODIFIED="1476104123018" TEXT="Implementa&#xe7;&#xe3;o parcial do Driver">
<attribute NAME="time" VALUE="10"/>
<node CREATED="1476103784268" ID="ID_1912683810" MODIFIED="1476103930549" TEXT="As queryes n&#xe3;o usam o novo Compiler defindo">
<icon BUILTIN="stop-sign"/>
</node>
<node CREATED="1476103856120" ID="ID_215599895" MODIFIED="1476103911431" TEXT="ContentTypes e Authentication d&#xe3;o problemas devido ao banco de dados (Arango sendo usado como &apos;default&apos;)">
<icon BUILTIN="messagebox_warning"/>
<node CREATED="1476103972593" ID="ID_886372032" MODIFIED="1476104012771" TEXT="Estudo de Models, multiple databases e Routers">
<attribute NAME="time" VALUE="10"/>
<node CREATED="1476104063384" ID="ID_312951136" MODIFIED="1476104316939" TEXT="Divis&#xe3;o em dois bds SQL cuida das tabelas internas e arango cuida das outras coisas">
<icon BUILTIN="idea"/>
</node>
<node CREATED="1476104205791" ID="ID_1816157403" MODIFIED="1476109774442" TEXT="Router Para definir que model usa qual BD">
<attribute NAME="time" VALUE="3"/>
</node>
<node CREATED="1476104269175" ID="ID_109996170" MODIFIED="1476104312266" TEXT="Como associar um usu&#xe1;rio no Arango com usu&#xe1;rio no SQL">
<icon BUILTIN="help"/>
</node>
</node>
</node>
</node>
<node CREATED="1476104127822" ID="ID_1342392825" MODIFIED="1476104140127" TEXT="Implementa&#xe7;&#xe3;o dos Models">
<node CREATED="1476109834667" ID="ID_1095389929" MODIFIED="1476109854004" TEXT="ModelAbstrato Node"/>
<node CREATED="1476109871430" ID="ID_932124584" MODIFIED="1476109878320" TEXT="ModelAbstratoBase"/>
<node CREATED="1476109855262" ID="ID_642789529" MODIFIED="1476109864277" TEXT="ModelAbstrato Edge"/>
<node CREATED="1476109924928" ID="ID_1864289481" MODIFIED="1476110274080" TEXT="Model Usa o Manager especial">
<arrowlink DESTINATION="ID_167372989" ENDARROW="None" ENDINCLINATION="205;0;" ID="Arrow_ID_127398090" STARTARROW="Default" STARTINCLINATION="205;0;"/>
</node>
</node>
<node CREATED="1476104150377" ID="ID_167372989" MODIFIED="1476110274080" TEXT="Implementa&#xe7;&#xe3;o dos Managers">
<linktarget COLOR="#b0b0b0" DESTINATION="ID_167372989" ENDARROW="None" ENDINCLINATION="205;0;" ID="Arrow_ID_127398090" SOURCE="ID_1864289481" STARTARROW="Default" STARTINCLINATION="205;0;"/>
</node>
<node CREATED="1476104160711" ID="ID_1305173548" MODIFIED="1476110121246" TEXT="Implementa&#xe7;&#xe3;o dos Fields"/>
</node>
</node>
</map>
