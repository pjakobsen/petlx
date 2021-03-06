"""
Tests for the gff3 module.

"""
from tempfile import NamedTemporaryFile
from nose.tools import eq_
from petl.util import header

from petlx.gff3 import fromgff3, gff3lookup, gff3join, gff3_parse_attributes,\
    gff3leftjoin
from petl.transform import selecteq
from petl.testutils import ieq
import petl.fluent as etl


plasmodb_gff3 = """
##gff-version	3
##feature-ontology	so.obo
##attribute-ontology	gff3_attributes.obo
##sequence-region	apidb|MAL1	1	643292
##sequence-region	apidb|MAL2	1	947102
##sequence-region	apidb|MAL3	1	1060087
##sequence-region	apidb|MAL4	1	1204112
##sequence-region	apidb|MAL5	1	1343552
##sequence-region	apidb|MAL6	1	1418244
##sequence-region	apidb|MAL7	1	1501717
##sequence-region	apidb|MAL8	1	1419563
##sequence-region	apidb|MAL9	1	1541723
##sequence-region	apidb|MAL10	1	1687655
##sequence-region	apidb|MAL11	1	2038337
##sequence-region	apidb|MAL12	1	2271478
##sequence-region	apidb|MAL13	1	2895605
##sequence-region	apidb|MAL14	1	3291871
##sequence-region	apidb|M76611	1	5967
##sequence-region	apidb|PfNF54	1	5967
##sequence-region	apidb|X95275	1	15421
##sequence-region	apidb|X95276	1	14009
##sequence-region	apidb|API_IRAB	1	34242
##sequence-region	apidb|NC_002375	1	5967
apidb|MAL1	ApiDB	supercontig	1	643292	.	+	.	ID=apidb|MAL1;Name=MAL1;description=MAL1;size=643292;web_id=MAL1;molecule_type=dsDNA;organism_name=Plasmodium falciparum;translation_table=11;topology=linear;localization=nuclear;Dbxref=ApiDB_PlasmoDB:MAL1,GenBank:NC_004325,taxon:36329
apidb|MAL2	ApiDB	supercontig	1	947102	.	+	.	ID=apidb|MAL2;Name=MAL2;description=MAL2;size=947102;web_id=MAL2;molecule_type=dsDNA;organism_name=Plasmodium falciparum;translation_table=11;topology=linear;localization=nuclear;Dbxref=ApiDB_PlasmoDB:MAL2,GenBank:NC_000910,taxon:36329;
apidb|MAL3	ApiDB	supercontig	1	1060087	.	+	.	ID=apidb|MAL3;Name=MAL3;description=MAL3;size=1060087;web_id=MAL3;molecule_type=dsDNA;organism_name=Plasmodium falciparum;translation_table=11;topology=linear;localization=nuclear;Dbxref=ApiDB_PlasmoDB:MAL3,GenBank:NC_000521,taxon:36329
apidb|MAL4	ApiDB	supercontig	1	1204112	.	+	.	ID=apidb|MAL4;Name=MAL4;description=MAL4;size=1204112;web_id=MAL4;molecule_type=dsDNA;organism_name=Plasmodium falciparum;translation_table=11;topology=linear;localization=nuclear;Dbxref=ApiDB_PlasmoDB:MAL4,GenBank:NC_004318,taxon:36329
apidb|MAL5	ApiDB	supercontig	1	1343552	.	+	.	ID=apidb|MAL5;Name=MAL5;description=MAL5;size=1343552;web_id=MAL5;molecule_type=dsDNA;organism_name=Plasmodium falciparum;translation_table=11;topology=linear;localization=nuclear;Dbxref=ApiDB_PlasmoDB:MAL5,GenBank:NC_004326,taxon:36329
apidb|MAL6	ApiDB	supercontig	1	1418244	.	+	.	ID=apidb|MAL6;Name=MAL6;description=MAL6;size=1418244;web_id=MAL6;molecule_type=dsDNA;organism_name=Plasmodium falciparum;translation_table=11;topology=linear;localization=nuclear;Dbxref=ApiDB_PlasmoDB:MAL6,GenBank:NC_004327,taxon:36329
apidb|MAL7	ApiDB	supercontig	1	1501717	.	+	.	ID=apidb|MAL7;Name=MAL7;description=MAL7;size=1501717;web_id=MAL7;molecule_type=dsDNA;organism_name=Plasmodium falciparum;translation_table=11;topology=linear;localization=nuclear;Dbxref=ApiDB_PlasmoDB:MAL7,GenBank:NC_004328,taxon:36329
apidb|MAL8	ApiDB	supercontig	1	1419563	.	+	.	ID=apidb|MAL8;Name=MAL8;description=MAL8;size=1419563;web_id=MAL8;molecule_type=dsDNA;organism_name=Plasmodium falciparum;translation_table=11;topology=linear;localization=nuclear;Dbxref=ApiDB_PlasmoDB:MAL8,GenBank:NC_004329,taxon:36329
apidb|MAL9	ApiDB	supercontig	1	1541723	.	+	.	ID=apidb|MAL9;Name=MAL9;description=MAL9;size=1541723;web_id=MAL9;molecule_type=dsDNA;organism_name=Plasmodium falciparum;translation_table=11;topology=linear;localization=nuclear;Dbxref=ApiDB_PlasmoDB:MAL9,GenBank:NC_004330,taxon:36329
apidb|MAL10	ApiDB	supercontig	1	1687655	.	+	.	ID=apidb|MAL10;Name=MAL10;description=MAL10;size=1687655;web_id=MAL10;molecule_type=dsDNA;organism_name=Plasmodium falciparum;translation_table=11;topology=linear;localization=nuclear;Dbxref=ApiDB_PlasmoDB:MAL10,GenBank:NC_004314,taxon:36329
apidb|MAL11	ApiDB	supercontig	1	2038337	.	+	.	ID=apidb|MAL11;Name=MAL11;description=MAL11;size=2038337;web_id=MAL11;molecule_type=dsDNA;organism_name=Plasmodium falciparum;translation_table=11;topology=linear;localization=nuclear;Dbxref=ApiDB_PlasmoDB:MAL11,GenBank:NC_004315,taxon:36329
apidb|MAL12	ApiDB	supercontig	1	2271478	.	+	.	ID=apidb|MAL12;Name=MAL12;description=MAL12;size=2271478;web_id=MAL12;molecule_type=dsDNA;organism_name=Plasmodium falciparum;translation_table=11;topology=linear;localization=nuclear;Dbxref=ApiDB_PlasmoDB:MAL12,GenBank:NC_004316,taxon:36329
apidb|MAL13	ApiDB	supercontig	1	2895605	.	+	.	ID=apidb|MAL13;Name=MAL13;description=MAL13;size=2895605;web_id=MAL13;molecule_type=dsDNA;organism_name=Plasmodium falciparum;translation_table=11;topology=linear;localization=nuclear;Dbxref=ApiDB_PlasmoDB:MAL13,GenBank:NC_004331,taxon:36329
apidb|MAL14	ApiDB	supercontig	1	3291871	.	+	.	ID=apidb|MAL14;Name=MAL14;description=MAL14;size=3291871;web_id=MAL14;molecule_type=dsDNA;organism_name=Plasmodium falciparum;translation_table=11;topology=linear;localization=nuclear;Dbxref=ApiDB_PlasmoDB:MAL14,GenBank:NC_004317,taxon:36329
apidb|M76611	ApiDB	supercontig	1	5967	.	+	.	ID=apidb|M76611;Name=M76611;description=M76611;size=5967;web_id=M76611;molecule_type=dsDNA;organism_name=Plasmodium falciparum;translation_table=11;topology=linear;localization=nuclear;Dbxref=ApiDB_PlasmoDB:M76611,taxon:36329
apidb|PfNF54	ApiDB	supercontig	1	5967	.	+	.	ID=apidb|PfNF54;Name=PfNF54;description=PfNF54;size=5967;web_id=PfNF54;molecule_type=dsDNA;organism_name=Plasmodium falciparum;translation_table=11;topology=linear;localization=nuclear;Dbxref=ApiDB_PlasmoDB:PfNF54,taxon:36329
apidb|X95275	ApiDB	supercontig	1	15421	.	+	.	ID=apidb|X95275;Name=X95275;description=Plasmodium+falciparum+complete+gene+map+of+plastid-like+DNA+%28IR-A%29.;size=15421;web_id=X95275;molecule_type=dsDNA;organism_name=Plasmodium falciparum;translation_table=11;topology=linear;localization=nuclear;Dbxref=ApiDB_PlasmoDB:X95275,GenBank:,taxon:36329
apidb|X95276	ApiDB	supercontig	1	14009	.	+	.	ID=apidb|X95276;Name=X95276;description=Plasmodium+falciparum+complete+gene+map+of+plastid-like+DNA+%28IR-B%29.;size=14009;web_id=X95276;molecule_type=dsDNA;organism_name=Plasmodium falciparum;translation_table=11;topology=linear;localization=nuclear;Dbxref=ApiDB_PlasmoDB:X95276,GenBank:,taxon:36329
apidb|API_IRAB	ApiDB	supercontig	1	34242	.	+	.	ID=apidb|API_IRAB;Name=API_IRAB;description=API_IRAB;size=34242;web_id=API_IRAB;molecule_type=dsDNA;organism_name=Plasmodium falciparum;translation_table=11;topology=linear;localization=nuclear;Dbxref=ApiDB_PlasmoDB:API_IRAB,taxon:36329
apidb|NC_002375	ApiDB	supercontig	1	5967	.	+	.	ID=apidb|NC_002375;Name=NC_002375;description=Plasmodium+falciparum+mitochondrion%2C+complete+genome.;size=5967;web_id=NC_002375;molecule_type=dsDNA;organism_name=Plasmodium falciparum;translation_table=11;topology=linear;localization=nuclear;Dbxref=ApiDB_PlasmoDB:NC_002375,GenBank:NC_002375,taxon:36329
apidb|NC_002375	ApiDB	gene	1933	3471	.	+	.	ID=apidb|coI;Name=coI;description=putative+cytochrome+oxidase+I;size=1539;web_id=coI;locus_tag=coI;size=1539;Alias=PlfaoMp2
apidb|NC_002375	ApiDB	mRNA	1933	3471	.	+	.	ID=apidb|rna_coI-1;Name=coI-1;description=putative+cytochrome+oxidase+I;size=1539;Parent=apidb|coI;Dbxref=ApiDB_PlasmoDB:coI,EC:1.9.3.1,taxon:36329
apidb|NC_002375	ApiDB	CDS	1933	3471	.	+	0	ID=apidb|cds_coI-1;Name=cds;description=.;size=1539;Parent=apidb|rna_coI-1
apidb|NC_002375	ApiDB	exon	1933	3471	.	+	.	ID=apidb|exon_coI-1;Name=exon;description=exon;size=1539;Parent=apidb|rna_coI-1
apidb|NC_002375	ApiDB	gene	3492	4622	.	+	.	ID=apidb|CYTB;Name=CYTB;description=cytochrome+b;size=1131;web_id=CYTB;locus_tag=CYTB;size=1131;Alias=PlfaoMp3
apidb|NC_002375	ApiDB	mRNA	3492	4622	.	+	.	ID=apidb|rna_CYTB-1;Name=CYTB-1;description=cytochrome+b;size=1131;Parent=apidb|CYTB;Dbxref=ApiDB_PlasmoDB:CYTB,taxon:36329
apidb|NC_002375	ApiDB	CDS	3492	4622	.	+	0	ID=apidb|cds_CYTB-1;Name=cds;description=.;size=1131;Parent=apidb|rna_CYTB-1
apidb|NC_002375	ApiDB	exon	3492	4622	.	+	.	ID=apidb|exon_CYTB-1;Name=exon;description=exon;size=1131;Parent=apidb|rna_CYTB-1
apidb|MAL14	ApiDB	gene	1889356	1889472	.	+	.	ID=apidb|U5RNA;Name=U5RNA;description=U5RNA;size=117;web_id=U5RNA;locus_tag=U5RNA;size=117
apidb|MAL14	ApiDB	mRNA	1889356	1889472	.	+	.	ID=apidb|rna_U5RNA-1;Name=U5RNA-1;description=U5RNA-1;size=117;Parent=apidb|U5RNA;Dbxref=ApiDB_PlasmoDB:U5RNA,taxon:36329
apidb|MAL14	ApiDB	CDS	1889356	1889472	.	+	0	ID=apidb|cds_U5RNA-1;Name=cds;description=.;size=117;Parent=apidb|rna_U5RNA-1
apidb|MAL14	ApiDB	exon	1889356	1889472	.	+	.	ID=apidb|exon_U5RNA-1;Name=exon;description=exon;size=117;Parent=apidb|rna_U5RNA-1
apidb|NC_002375	ApiDB	gene	734	1573	.	-	.	ID=apidb|coxIII;Name=coxIII;description=putative+cytochrome+oxidase+III;size=840;web_id=coxIII;locus_tag=coxIII;size=840;Alias=PlfaoMp1
apidb|NC_002375	ApiDB	mRNA	734	1573	.	-	.	ID=apidb|rna_coxIII-1;Name=coxIII-1;description=putative+cytochrome+oxidase+III;size=840;Parent=apidb|coxIII;Dbxref=ApiDB_PlasmoDB:coxIII,EC:1.9.3.1,taxon:36329
apidb|NC_002375	ApiDB	CDS	734	1573	.	-	0	ID=apidb|cds_coxIII-1;Name=cds;description=.;size=840;Parent=apidb|rna_coxIII-1
apidb|NC_002375	ApiDB	exon	734	1573	.	-	.	ID=apidb|exon_coxIII-1;Name=exon;description=exon;size=840;Parent=apidb|rna_coxIII-1
apidb|MAL1	ApiDB	gene	474888	477036	.	+	.	ID=apidb|MAL1_18s;Name=MAL1_18s;description=18s+rRNA+A-type;size=2149;web_id=MAL1_18s;locus_tag=MAL1_18s;size=2149
apidb|MAL1	ApiDB	rRNA	474888	477036	.	+	.	ID=apidb|rna_MAL1_18s-1;Name=MAL1_18s-1;description=18s+rRNA+A-type;size=2149;Parent=apidb|MAL1_18s;Dbxref=ApiDB_PlasmoDB:MAL1_18s,Sanger:MAL1_18s,taxon:36329
apidb|MAL1	ApiDB	exon	474888	477036	.	+	.	ID=apidb|exon_MAL1_18s-1;Name=exon;description=exon;size=2149;Parent=apidb|rna_MAL1_18s-1
apidb|MAL1	ApiDB	gene	478428	482531	.	+	.	ID=apidb|MAL1_28s;Name=MAL1_28s;description=28s+rRNA+%28A-type%29;size=4104;web_id=MAL1_28s;locus_tag=MAL1_28s;size=4104
apidb|MAL1	ApiDB	rRNA	478428	482531	.	+	.	ID=apidb|rna_MAL1_28s-1;Name=MAL1_28s-1;description=28s+rRNA+%28A-type%29;size=4104;Parent=apidb|MAL1_28s;Dbxref=ApiDB_PlasmoDB:MAL1_28s,Sanger:MAL1_28s,taxon:36329
apidb|MAL1	ApiDB	exon	478428	482531	.	+	.	ID=apidb|exon_MAL1_28s-1;Name=exon;description=exon;size=4104;Parent=apidb|rna_MAL1_28s-1
apidb|MAL5	ApiDB	gene	1289594	1291685	.	+	.	ID=apidb|MAL5_18S;Name=MAL5_18S;description=MAL5_18S;size=2092;web_id=MAL5_18S;locus_tag=MAL5_18S;size=2092
apidb|MAL5	ApiDB	rRNA	1289594	1291685	.	+	.	ID=apidb|rna_MAL5_18S-1;Name=MAL5_18S-1;description=MAL5_18S-1;size=2092;Parent=apidb|MAL5_18S;Dbxref=ApiDB_PlasmoDB:MAL5_18S,Sanger:MAL5_18S,taxon:36329
apidb|MAL5	ApiDB	exon	1289594	1291685	.	+	.	ID=apidb|exon_MAL5_18S-1;Name=exon;description=exon;size=2092;Parent=apidb|rna_MAL5_18S-1
apidb|MAL5	ApiDB	gene	1292403	1296192	.	+	.	ID=apidb|MAL5_28S;Name=MAL5_28S;description=MAL5_28S;size=3790;web_id=MAL5_28S;locus_tag=MAL5_28S;size=3790
apidb|MAL5	ApiDB	rRNA	1292403	1296192	.	+	.	ID=apidb|rna_MAL5_28S-1;Name=MAL5_28S-1;description=MAL5_28S-1;size=3790;Parent=apidb|MAL5_28S;Dbxref=ApiDB_PlasmoDB:MAL5_28S,Sanger:MAL5_28S,taxon:36329
apidb|MAL5	ApiDB	exon	1292403	1296192	.	+	.	ID=apidb|exon_MAL5_28S-1;Name=exon;description=exon;size=3790;Parent=apidb|rna_MAL5_28S-1
apidb|MAL7	ApiDB	gene	121104	122236	.	-	.	ID=apidb|MAL7P1.3;Name=MAL7P1.3;description=hypothetical+protein%2C+conserved+in+P.+falciparum;size=1133;web_id=MAL7P1.3;locus_tag=MAL7P1.3;size=1133
apidb|MAL7	ApiDB	mRNA	121104	122236	.	-	.	ID=apidb|rna_MAL7P1.3-1;Name=MAL7P1.3-1;description=hypothetical+protein%2C+conserved+in+P.+falciparum;size=1133;Parent=apidb|MAL7P1.3;Dbxref=ApiDB_PlasmoDB:MAL7P1.3,Sanger:MAL7P1.3,taxon:36329
apidb|MAL7	ApiDB	CDS	122168	122236	.	-	0	ID=apidb|cds_MAL7P1.3-1;Name=cds;description=.;size=69;Parent=apidb|rna_MAL7P1.3-1
apidb|MAL7	ApiDB	CDS	121836	121959	.	-	0	ID=apidb|cds_MAL7P1.3-1;Name=cds;description=.;size=124;Parent=apidb|rna_MAL7P1.3-1
apidb|MAL7	ApiDB	CDS	121104	121690	.	-	2	ID=apidb|cds_MAL7P1.3-1;Name=cds;description=.;size=587;Parent=apidb|rna_MAL7P1.3-1
apidb|MAL7	ApiDB	exon	122168	122236	.	-	.	ID=apidb|exon_MAL7P1.3-1;Name=exon;description=exon;size=69;Parent=apidb|rna_MAL7P1.3-1
apidb|MAL7	ApiDB	exon	121836	121959	.	-	.	ID=apidb|exon_MAL7P1.3-2;Name=exon;description=exon;size=124;Parent=apidb|rna_MAL7P1.3-1
apidb|MAL7	ApiDB	exon	121104	121690	.	-	.	ID=apidb|exon_MAL7P1.3-3;Name=exon;description=exon;size=587;Parent=apidb|rna_MAL7P1.3-1
apidb|MAL7	ApiDB	gene	123448	124216	.	+	.	ID=apidb|MAL7P1.4;Name=MAL7P1.4;description=hypothetical+protein%2C+conserved+in+P.+falciparum;size=769;web_id=MAL7P1.4;locus_tag=MAL7P1.4;size=769
apidb|MAL7	ApiDB	mRNA	123448	124216	.	+	.	ID=apidb|rna_MAL7P1.4-1;Name=MAL7P1.4-1;description=hypothetical+protein%2C+conserved+in+P.+falciparum;size=769;Parent=apidb|MAL7P1.4;Dbxref=ApiDB_PlasmoDB:MAL7P1.4,Sanger:MAL7P1.4,taxon:36329
apidb|MAL7	ApiDB	CDS	123448	123516	.	+	0	ID=apidb|cds_MAL7P1.4-1;Name=cds;description=.;size=69;Parent=apidb|rna_MAL7P1.4-1
apidb|MAL7	ApiDB	CDS	123593	124216	.	+	0	ID=apidb|cds_MAL7P1.4-1;Name=cds;description=.;size=624;Parent=apidb|rna_MAL7P1.4-1
apidb|MAL7	ApiDB	exon	123448	123516	.	+	.	ID=apidb|exon_MAL7P1.4-1;Name=exon;description=exon;size=69;Parent=apidb|rna_MAL7P1.4-1
apidb|MAL7	ApiDB	exon	123593	124216	.	+	.	ID=apidb|exon_MAL7P1.4-2;Name=exon;description=exon;size=624;Parent=apidb|rna_MAL7P1.4-1
apidb|MAL7	ApiDB	gene	126425	127236	.	+	.	ID=apidb|MAL7P1.5;Name=MAL7P1.5;description=Plasmodium+falciparum+Maurer%27s+Cleft+2+transmembrane+domain+protein%2C+PfMC-2TM_7.1;size=812;web_id=MAL7P1.5;locus_tag=MAL7P1.5;size=812
apidb|MAL7	ApiDB	mRNA	126425	127236	.	+	.	ID=apidb|rna_MAL7P1.5-1;Name=MAL7P1.5-1;description=Plasmodium+falciparum+Maurer%27s+Cleft+2+transmembrane+domain+protein%2C+PfMC-2TM_7.1;size=812;Parent=apidb|MAL7P1.5;Dbxref=ApiDB_PlasmoDB:MAL7P1.5,NCBI_gi:124511636,NCBI_gi:23498719,Sanger:MAL7P1.5,taxon:36329
apidb|MAL7	ApiDB	CDS	126425	126493	.	+	0	ID=apidb|cds_MAL7P1.5-1;Name=cds;description=.;size=69;Parent=apidb|rna_MAL7P1.5-1
apidb|MAL7	ApiDB	CDS	126598	127236	.	+	0	ID=apidb|cds_MAL7P1.5-1;Name=cds;description=.;size=639;Parent=apidb|rna_MAL7P1.5-1
apidb|MAL7	ApiDB	exon	126425	126493	.	+	.	ID=apidb|exon_MAL7P1.5-1;Name=exon;description=exon;size=69;Parent=apidb|rna_MAL7P1.5-1
apidb|MAL7	ApiDB	exon	126598	127236	.	+	.	ID=apidb|exon_MAL7P1.5-2;Name=exon;description=exon;size=639;Parent=apidb|rna_MAL7P1.5-1
apidb|MAL7	ApiDB	gene	140158	141050	.	+	.	ID=apidb|MAL7P1.6;Name=MAL7P1.6;description=hypothetical+protein%2C+conserved+in+P.falciparum;size=893;web_id=MAL7P1.6;locus_tag=MAL7P1.6;size=893
apidb|MAL7	ApiDB	mRNA	140158	141050	.	+	.	ID=apidb|rna_MAL7P1.6-1;Name=MAL7P1.6-1;description=hypothetical+protein%2C+conserved+in+P.falciparum;size=893;Parent=apidb|MAL7P1.6;Ontology_term=GO:0020011;Dbxref=ApiDB_PlasmoDB:MAL7P1.6,NCBI_gi:124511644,NCBI_gi:23498723,Sanger:MAL7P1.6,taxon:36329
apidb|MAL7	ApiDB	CDS	140158	140226	.	+	0	ID=apidb|cds_MAL7P1.6-1;Name=cds;description=.;size=69;Parent=apidb|rna_MAL7P1.6-1
apidb|MAL7	ApiDB	CDS	140367	141050	.	+	0	ID=apidb|cds_MAL7P1.6-1;Name=cds;description=.;size=684;Parent=apidb|rna_MAL7P1.6-1
apidb|MAL7	ApiDB	exon	140158	140226	.	+	.	ID=apidb|exon_MAL7P1.6-1;Name=exon;description=exon;size=69;Parent=apidb|rna_MAL7P1.6-1
apidb|MAL7	ApiDB	exon	140367	141050	.	+	.	ID=apidb|exon_MAL7P1.6-2;Name=exon;description=exon;size=684;Parent=apidb|rna_MAL7P1.6-1
apidb|MAL7	ApiDB	gene	144051	146252	.	+	.	ID=apidb|MAL7P1.7;Name=MAL7P1.7;description=RESA-like+protein;size=2202;web_id=MAL7P1.7;locus_tag=MAL7P1.7;size=2202
apidb|MAL7	ApiDB	mRNA	144051	146252	.	+	.	ID=apidb|rna_MAL7P1.7-1;Name=MAL7P1.7-1;description=RESA-like+protein;size=2202;Parent=apidb|MAL7P1.7;Dbxref=ApiDB_PlasmoDB:MAL7P1.7,NCBI_gi:124511646,NCBI_gi:23498724,Sanger:MAL7P1.7,taxon:36329
apidb|MAL7	ApiDB	CDS	144051	144236	.	+	0	ID=apidb|cds_MAL7P1.7-1;Name=cds;description=.;size=186;Parent=apidb|rna_MAL7P1.7-1
apidb|MAL7	ApiDB	CDS	144422	145151	.	+	0	ID=apidb|cds_MAL7P1.7-1;Name=cds;description=.;size=730;Parent=apidb|rna_MAL7P1.7-1
apidb|MAL7	ApiDB	CDS	145327	146252	.	+	2	ID=apidb|cds_MAL7P1.7-1;Name=cds;description=.;size=926;Parent=apidb|rna_MAL7P1.7-1
apidb|MAL7	ApiDB	exon	144051	144236	.	+	.	ID=apidb|exon_MAL7P1.7-1;Name=exon;description=exon;size=186;Parent=apidb|rna_MAL7P1.7-1
apidb|MAL7	ApiDB	exon	144422	145151	.	+	.	ID=apidb|exon_MAL7P1.7-2;Name=exon;description=exon;size=730;Parent=apidb|rna_MAL7P1.7-1
apidb|MAL7	ApiDB	exon	145327	146252	.	+	.	ID=apidb|exon_MAL7P1.7-3;Name=exon;description=exon;size=926;Parent=apidb|rna_MAL7P1.7-1
apidb|MAL7	ApiDB	gene	1139137	1139564	.	+	.	ID=apidb|MAL7_18S;Name=MAL7_18S;description=MAL7_18S;size=428;web_id=MAL7_18S;locus_tag=MAL7_18S;size=428
apidb|MAL7	ApiDB	rRNA	1139137	1139564	.	+	.	ID=apidb|rna_MAL7_18S-1;Name=MAL7_18S-1;description=MAL7_18S-1;size=428;Parent=apidb|MAL7_18S;Dbxref=ApiDB_PlasmoDB:MAL7_18S,Sanger:MAL7_18S,taxon:36329
apidb|MAL7	ApiDB	exon	1139137	1139564	.	+	.	ID=apidb|exon_MAL7_18S-1;Name=exon;description=exon;size=428;Parent=apidb|rna_MAL7_18S-1
apidb|MAL7	ApiDB	gene	1141946	1144480	.	+	.	ID=apidb|MAL7_28S;Name=MAL7_28S;description=MAL7_28S;size=2535;web_id=MAL7_28S;locus_tag=MAL7_28S;size=2535
apidb|MAL7	ApiDB	rRNA	1141946	1144480	.	+	.	ID=apidb|rna_MAL7_28S-1;Name=MAL7_28S-1;description=MAL7_28S-1;size=2535;Parent=apidb|MAL7_28S;Dbxref=ApiDB_PlasmoDB:MAL7_28S,Sanger:MAL7_28S,taxon:36329
apidb|MAL7	ApiDB	exon	1141946	1144480	.	+	.	ID=apidb|exon_MAL7_28S-1;Name=exon;description=exon;size=2535;Parent=apidb|rna_MAL7_28S-1
apidb|MAL8	ApiDB	gene	1326215	1332258	.	+	.	ID=apidb|MAL8P1.1;Name=MAL8P1.1;description=surface-associated+interspersed+gene+8.1%2C+%28SURFIN8.1%29;size=6044;web_id=MAL8P1.1;locus_tag=MAL8P1.1;size=6044
apidb|MAL8	ApiDB	mRNA	1326215	1332258	.	+	.	ID=apidb|rna_MAL8P1.1-1;Name=MAL8P1.1-1;description=surface-associated+interspersed+gene+8.1%2C+%28SURFIN8.1%29;size=6044;Parent=apidb|MAL8P1.1;Dbxref=ApiDB_PlasmoDB:MAL8P1.1,Sanger:MAL8P1.1,taxon:36329
apidb|MAL8	ApiDB	CDS	1326215	1327079	.	+	0	ID=apidb|cds_MAL8P1.1-1;Name=cds;description=.;size=865;Parent=apidb|rna_MAL8P1.1-1
apidb|MAL8	ApiDB	CDS	1327247	1327473	.	+	2	ID=apidb|cds_MAL8P1.1-1;Name=cds;description=.;size=227;Parent=apidb|rna_MAL8P1.1-1
apidb|MAL8	ApiDB	CDS	1327585	1332258	.	+	0	ID=apidb|cds_MAL8P1.1-1;Name=cds;description=.;size=4674;Parent=apidb|rna_MAL8P1.1-1
apidb|MAL8	ApiDB	exon	1326215	1327079	.	+	.	ID=apidb|exon_MAL8P1.1-1;Name=exon;description=exon;size=865;Parent=apidb|rna_MAL8P1.1-1
apidb|MAL8	ApiDB	exon	1327247	1327473	.	+	.	ID=apidb|exon_MAL8P1.1-2;Name=exon;description=exon;size=227;Parent=apidb|rna_MAL8P1.1-1
apidb|MAL8	ApiDB	exon	1327585	1332258	.	+	.	ID=apidb|exon_MAL8P1.1-3;Name=exon;description=exon;size=4674;Parent=apidb|rna_MAL8P1.1-1
apidb|MAL8	ApiDB	gene	1322488	1323896	.	+	.	ID=apidb|MAL8P1.2;Name=MAL8P1.2;description=hypothetical+protein%2C+conserved+in+P.falciparum;size=1409;web_id=MAL8P1.2;locus_tag=MAL8P1.2;size=1409
apidb|MAL8	ApiDB	mRNA	1322488	1323896	.	+	.	ID=apidb|rna_MAL8P1.2-1;Name=MAL8P1.2-1;description=hypothetical+protein%2C+conserved+in+P.falciparum;size=1409;Parent=apidb|MAL8P1.2;Dbxref=ApiDB_PlasmoDB:MAL8P1.2,NCBI_gi:124512176,NCBI_gi:23498990,Sanger:MAL8P1.2,taxon:36329
apidb|MAL8	ApiDB	CDS	1322488	1322694	.	+	0	ID=apidb|cds_MAL8P1.2-1;Name=cds;description=.;size=207;Parent=apidb|rna_MAL8P1.2-1
apidb|MAL8	ApiDB	CDS	1322823	1323896	.	+	0	ID=apidb|cds_MAL8P1.2-1;Name=cds;description=.;size=1074;Parent=apidb|rna_MAL8P1.2-1
apidb|MAL8	ApiDB	exon	1322488	1322694	.	+	.	ID=apidb|exon_MAL8P1.2-1;Name=exon;description=exon;size=207;Parent=apidb|rna_MAL8P1.2-1
apidb|MAL8	ApiDB	exon	1322823	1323896	.	+	.	ID=apidb|exon_MAL8P1.2-2;Name=exon;description=exon;size=1074;Parent=apidb|rna_MAL8P1.2-1
apidb|MAL8	ApiDB	gene	1308124	1308995	.	+	.	ID=apidb|MAL8P1.3;Name=MAL8P1.3;description=integral+membrane+protein%2C+conserved+in+P.+falciparum;size=872;web_id=MAL8P1.3;locus_tag=MAL8P1.3;size=872
apidb|MAL8	ApiDB	mRNA	1308124	1308995	.	+	.	ID=apidb|rna_MAL8P1.3-1;Name=MAL8P1.3-1;description=integral+membrane+protein%2C+conserved+in+P.+falciparum;size=872;Parent=apidb|MAL8P1.3;Ontology_term=GO:0016021;Dbxref=ApiDB_PlasmoDB:MAL8P1.3,NCBI_gi:124512182,NCBI_gi:23498993,Sanger:MAL8P1.3,taxon:36329
apidb|MAL8	ApiDB	CDS	1308124	1308234	.	+	0	ID=apidb|cds_MAL8P1.3-1;Name=cds;description=.;size=111;Parent=apidb|rna_MAL8P1.3-1
apidb|MAL8	ApiDB	CDS	1308450	1308995	.	+	0	ID=apidb|cds_MAL8P1.3-1;Name=cds;description=.;size=546;Parent=apidb|rna_MAL8P1.3-1
apidb|MAL8	ApiDB	exon	1308124	1308234	.	+	.	ID=apidb|exon_MAL8P1.3-1;Name=exon;description=exon;size=111;Parent=apidb|rna_MAL8P1.3-1
apidb|MAL8	ApiDB	exon	1308450	1308995	.	+	.	ID=apidb|exon_MAL8P1.3-2;Name=exon;description=exon;size=546;Parent=apidb|rna_MAL8P1.3-1
apidb|MAL8	ApiDB	gene	1304394	1305884	.	+	.	ID=apidb|MAL8P1.4;Name=MAL8P1.4;description=hypothetical+protein%2C+conserved;size=1491;web_id=MAL8P1.4;locus_tag=MAL8P1.4;size=1491
apidb|MAL8	ApiDB	mRNA	1304394	1305884	.	+	.	ID=apidb|rna_MAL8P1.4-1;Name=MAL8P1.4-1;description=hypothetical+protein%2C+conserved;size=1491;Parent=apidb|MAL8P1.4;Dbxref=ApiDB_PlasmoDB:MAL8P1.4,NCBI_gi:124512184,NCBI_gi:23498994,Sanger:MAL8P1.4,taxon:36329
apidb|MAL8	ApiDB	CDS	1304394	1304543	.	+	0	ID=apidb|cds_MAL8P1.4-1;Name=cds;description=.;size=150;Parent=apidb|rna_MAL8P1.4-1
apidb|MAL8	ApiDB	CDS	1304664	1305884	.	+	0	ID=apidb|cds_MAL8P1.4-1;Name=cds;description=.;size=1221;Parent=apidb|rna_MAL8P1.4-1
apidb|MAL8	ApiDB	exon	1304394	1304543	.	+	.	ID=apidb|exon_MAL8P1.4-1;Name=exon;description=exon;size=150;Parent=apidb|rna_MAL8P1.4-1
apidb|MAL8	ApiDB	exon	1304664	1305884	.	+	.	ID=apidb|exon_MAL8P1.4-2;Name=exon;description=exon;size=1221;Parent=apidb|rna_MAL8P1.4-1
apidb|MAL8	ApiDB	gene	1270206	1270718	.	+	.	ID=apidb|MAL8P1.6;Name=MAL8P1.6;description=early+transcribed+membrane+protein+8%2C+ETRAMP+8;size=513;web_id=MAL8P1.6;locus_tag=MAL8P1.6;size=513;Alias=etramp.BLOB.2
apidb|MAL8	ApiDB	mRNA	1270206	1270718	.	+	.	ID=apidb|rna_MAL8P1.6-1;Name=MAL8P1.6-1;description=early+transcribed+membrane+protein+8%2C+ETRAMP+8;size=513;Parent=apidb|MAL8P1.6;Dbxref=ApiDB_PlasmoDB:MAL8P1.6,Sanger:MAL8P1.6,taxon:36329
apidb|MAL8	ApiDB	CDS	1270206	1270718	.	+	0	ID=apidb|cds_MAL8P1.6-1;Name=cds;description=.;size=513;Parent=apidb|rna_MAL8P1.6-1
apidb|MAL8	ApiDB	exon	1270206	1270718	.	+	.	ID=apidb|exon_MAL8P1.6-1;Name=exon;description=exon;size=513;Parent=apidb|rna_MAL8P1.6-1
apidb|MAL8	ApiDB	gene	1261119	1267769	.	-	.	ID=apidb|MAL8P1.7;Name=MAL8P1.7;description=hypothetical+protein;size=6651;web_id=MAL8P1.7;locus_tag=MAL8P1.7;size=6651
apidb|MAL8	ApiDB	mRNA	1261119	1267769	.	-	.	ID=apidb|rna_MAL8P1.7-1;Name=MAL8P1.7-1;description=hypothetical+protein;size=6651;Parent=apidb|MAL8P1.7;Dbxref=ApiDB_PlasmoDB:MAL8P1.7,Sanger:MAL8P1.7,taxon:36329
apidb|MAL8	ApiDB	CDS	1266176	1267769	.	-	0	ID=apidb|cds_MAL8P1.7-1;Name=cds;description=.;size=1594;Parent=apidb|rna_MAL8P1.7-1
apidb|MAL8	ApiDB	CDS	1264040	1266037	.	-	2	ID=apidb|cds_MAL8P1.7-1;Name=cds;description=.;size=1998;Parent=apidb|rna_MAL8P1.7-1
apidb|MAL8	ApiDB	CDS	1261119	1263919	.	-	2	ID=apidb|cds_MAL8P1.7-1;Name=cds;description=.;size=2801;Parent=apidb|rna_MAL8P1.7-1
apidb|MAL8	ApiDB	exon	1266176	1267769	.	-	.	ID=apidb|exon_MAL8P1.7-1;Name=exon;description=exon;size=1594;Parent=apidb|rna_MAL8P1.7-1
apidb|MAL8	ApiDB	exon	1264040	1266037	.	-	.	ID=apidb|exon_MAL8P1.7-2;Name=exon;description=exon;size=1998;Parent=apidb|rna_MAL8P1.7-1
apidb|MAL8	ApiDB	exon	1261119	1263919	.	-	.	ID=apidb|exon_MAL8P1.7-3;Name=exon;description=exon;size=2801;Parent=apidb|rna_MAL8P1.7-1
apidb|MAL8	ApiDB	gene	1258562	1260112	.	-	.	ID=apidb|MAL8P1.8;Name=MAL8P1.8;description=hypothetical+protein%2C+conserved;size=1551;web_id=MAL8P1.8;locus_tag=MAL8P1.8;size=1551
apidb|MAL8	ApiDB	mRNA	1258562	1260112	.	-	.	ID=apidb|rna_MAL8P1.8-1;Name=MAL8P1.8-1;description=hypothetical+protein%2C+conserved;size=1551;Parent=apidb|MAL8P1.8;Ontology_term=GO:0019538,GO:0016706;Dbxref=ApiDB_PlasmoDB:MAL8P1.8,EC:1.14.11.2,NCBI_gi:124512198,NCBI_gi:23499001,Sanger:MAL8P1.8,taxon:36329
apidb|MAL8	ApiDB	CDS	1258842	1260112	.	-	0	ID=apidb|cds_MAL8P1.8-1;Name=cds;description=.;size=1271;Parent=apidb|rna_MAL8P1.8-1
apidb|MAL8	ApiDB	CDS	1258562	1258607	.	-	1	ID=apidb|cds_MAL8P1.8-1;Name=cds;description=.;size=46;Parent=apidb|rna_MAL8P1.8-1
apidb|MAL8	ApiDB	exon	1258842	1260112	.	-	.	ID=apidb|exon_MAL8P1.8-1;Name=exon;description=exon;size=1271;Parent=apidb|rna_MAL8P1.8-1
apidb|MAL8	ApiDB	exon	1258562	1258607	.	-	.	ID=apidb|exon_MAL8P1.8-2;Name=exon;description=exon;size=46;Parent=apidb|rna_MAL8P1.8-1
apidb|MAL8	ApiDB	gene	1257626	1258096	.	+	.	ID=apidb|MAL8P1.9;Name=MAL8P1.9;description=u6+snRNA-associated+sm-like+protein%2C+putative;size=471;web_id=MAL8P1.9;locus_tag=MAL8P1.9;size=471
apidb|MAL8	ApiDB	mRNA	1257626	1258096	.	+	.	ID=apidb|rna_MAL8P1.9-1;Name=MAL8P1.9-1;description=u6+snRNA-associated+sm-like+protein%2C+putative;size=471;Parent=apidb|MAL8P1.9;Ontology_term=GO:0000398,GO:0016071,GO:0005732,GO:0030529,GO:0017070;Dbxref=ApiDB_PlasmoDB:MAL8P1.9,NCBI_gi:124512200,NCBI_gi:23499002,Sanger:MAL8P1.9,taxon:36329
apidb|MAL8	ApiDB	CDS	1257626	1257659	.	+	0	ID=apidb|cds_MAL8P1.9-1;Name=cds;description=.;size=34;Parent=apidb|rna_MAL8P1.9-1
apidb|MAL8	ApiDB	CDS	1257751	1257913	.	+	2	ID=apidb|cds_MAL8P1.9-1;Name=cds;description=.;size=163;Parent=apidb|rna_MAL8P1.9-1
apidb|MAL8	ApiDB	CDS	1258009	1258096	.	+	1	ID=apidb|cds_MAL8P1.9-1;Name=cds;description=.;size=88;Parent=apidb|rna_MAL8P1.9-1
apidb|MAL8	ApiDB	exon	1257626	1257659	.	+	.	ID=apidb|exon_MAL8P1.9-1;Name=exon;description=exon;size=34;Parent=apidb|rna_MAL8P1.9-1
apidb|MAL8	ApiDB	exon	1257751	1257913	.	+	.	ID=apidb|exon_MAL8P1.9-2;Name=exon;description=exon;size=163;Parent=apidb|rna_MAL8P1.9-1
apidb|MAL8	ApiDB	exon	1258009	1258096	.	+	.	ID=apidb|exon_MAL8P1.9-3;Name=exon;description=exon;size=88;Parent=apidb|rna_MAL8P1.9-1
apidb|MAL1	ApiDB	gene	29733	37349	.	+	.	ID=apidb|PFA0005w;Name=PFA0005w;description=erythrocyte+membrane+protein+1+%28PfEMP1%29;size=7617;web_id=PFA0005w;locus_tag=PFA0005w;size=7617;Alias=MAL1P4.01
apidb|MAL1	ApiDB	mRNA	29733	37349	.	+	.	ID=apidb|rna_PFA0005w-1;Name=PFA0005w-1;description=erythrocyte+membrane+protein+1+%28PfEMP1%29;size=7617;Parent=apidb|PFA0005w;Ontology_term=GO:0008152,GO:0009405,GO:0016337,GO:0020013,GO:0020033,GO:0020035,GO:0016021,GO:0020002,GO:0020030,GO:0003824,GO:0004872,GO:0005539,GO:0050839;Dbxref=ApiDB_PlasmoDB:PFA0005w,NCBI_gi:124505645,NCBI_gi:7670005,Sanger:PFA0005w,taxon:36329
apidb|MAL1	ApiDB	CDS	29733	34985	.	+	0	ID=apidb|cds_PFA0005w-1;Name=cds;description=.;size=5253;Parent=apidb|rna_PFA0005w-1
apidb|MAL1	ApiDB	CDS	36111	37349	.	+	0	ID=apidb|cds_PFA0005w-1;Name=cds;description=.;size=1239;Parent=apidb|rna_PFA0005w-1
apidb|MAL1	ApiDB	exon	29733	34985	.	+	.	ID=apidb|exon_PFA0005w-1;Name=exon;description=exon;size=5253;Parent=apidb|rna_PFA0005w-1
apidb|MAL1	ApiDB	exon	36111	37349	.	+	.	ID=apidb|exon_PFA0005w-2;Name=exon;description=exon;size=1239;Parent=apidb|rna_PFA0005w-1
apidb|MAL1	ApiDB	gene	39205	40430	.	-	.	ID=apidb|PFA0010c;Name=PFA0010c;description=rifin;size=1226;web_id=PFA0010c;locus_tag=PFA0010c;size=1226;Alias=MAL1P4.02
apidb|MAL1	ApiDB	mRNA	39205	40430	.	-	.	ID=apidb|rna_PFA0010c-1;Name=PFA0010c-1;description=rifin;size=1226;Parent=apidb|PFA0010c;Ontology_term=GO:0020033,GO:0016020,GO:0020002,GO:0003674;Dbxref=ApiDB_PlasmoDB:PFA0010c,NCBI_gi:124505647,NCBI_gi:7670006,Sanger:PFA0010c,taxon:36329
apidb|MAL1	ApiDB	CDS	40377	40430	.	-	0	ID=apidb|cds_PFA0010c-1;Name=cds;description=.;size=54;Parent=apidb|rna_PFA0010c-1
apidb|MAL1	ApiDB	CDS	39205	40146	.	-	0	ID=apidb|cds_PFA0010c-1;Name=cds;description=.;size=942;Parent=apidb|rna_PFA0010c-1
apidb|MAL1	ApiDB	exon	40377	40430	.	-	.	ID=apidb|exon_PFA0010c-1;Name=exon;description=exon;size=54;Parent=apidb|rna_PFA0010c-1
apidb|MAL1	ApiDB	exon	39205	40146	.	-	.	ID=apidb|exon_PFA0010c-2;Name=exon;description=exon;size=942;Parent=apidb|rna_PFA0010c-1
apidb|MAL1	ApiDB	gene	42590	46730	.	-	.	ID=apidb|PFA0015c;Name=PFA0015c;description=var-like+protein;size=4141;web_id=PFA0015c;locus_tag=PFA0015c;size=4141;Alias=MAL1P4.03
apidb|MAL1	ApiDB	mRNA	42590	46730	.	-	.	ID=apidb|rna_PFA0015c-1;Name=PFA0015c-1;description=var-like+protein;size=4141;Parent=apidb|PFA0015c;Ontology_term=GO:0009405,GO:0016021,GO:0004872;Dbxref=ApiDB_PlasmoDB:PFA0015c,NCBI_gi:124505649,NCBI_gi:7670007,Sanger:PFA0015c,taxon:36329
apidb|MAL1	ApiDB	CDS	43998	46730	.	-	0	ID=apidb|cds_PFA0015c-1;Name=cds;description=.;size=2733;Parent=apidb|rna_PFA0015c-1
apidb|MAL1	ApiDB	CDS	42590	43840	.	-	0	ID=apidb|cds_PFA0015c-1;Name=cds;description=.;size=1251;Parent=apidb|rna_PFA0015c-1
apidb|MAL1	ApiDB	exon	43998	46730	.	-	.	ID=apidb|exon_PFA0015c-1;Name=exon;description=exon;size=2733;Parent=apidb|rna_PFA0015c-1
apidb|MAL1	ApiDB	exon	42590	43840	.	-	.	ID=apidb|exon_PFA0015c-2;Name=exon;description=exon;size=1251;Parent=apidb|rna_PFA0015c-1
apidb|MAL1	ApiDB	gene	50586	51859	.	+	.	ID=apidb|PFA0020w;Name=PFA0020w;description=rifin;size=1274;web_id=PFA0020w;locus_tag=PFA0020w;size=1274;Alias=MAL1P4.04
apidb|MAL1	ApiDB	mRNA	50586	51859	.	+	.	ID=apidb|rna_PFA0020w-1;Name=PFA0020w-1;description=rifin;size=1274;Parent=apidb|PFA0020w;Ontology_term=GO:0020033,GO:0016020,GO:0020002,GO:0003674;Dbxref=ApiDB_PlasmoDB:PFA0020w,NCBI_gi:124505651,NCBI_gi:7670008,Sanger:PFA0020w,taxon:36329
apidb|MAL1	ApiDB	CDS	50586	50639	.	+	0	ID=apidb|cds_PFA0020w-1;Name=cds;description=.;size=54;Parent=apidb|rna_PFA0020w-1
apidb|MAL1	ApiDB	CDS	50795	51859	.	+	0	ID=apidb|cds_PFA0020w-1;Name=cds;description=.;size=1065;Parent=apidb|rna_PFA0020w-1
apidb|MAL1	ApiDB	exon	50586	50639	.	+	.	ID=apidb|exon_PFA0020w-1;Name=exon;description=exon;size=54;Parent=apidb|rna_PFA0020w-1
apidb|MAL1	ApiDB	exon	50795	51859	.	+	.	ID=apidb|exon_PFA0020w-2;Name=exon;description=exon;size=1065;Parent=apidb|rna_PFA0020w-1
apidb|MAL1	ApiDB	gene	53392	53503	.	-	.	ID=apidb|PFA0025c;Name=PFA0025c;description=erythrocyte+membrane+protein+1+%28PfEMP1%29+pseudogene;size=112;web_id=PFA0025c;locus_tag=PFA0025c;size=112;Alias=MAL1P4.05
apidb|MAL1	ApiDB	mRNA	53392	53503	.	-	.	ID=apidb|rna_PFA0025c-1;Name=PFA0025c-1;description=erythrocyte+membrane+protein+1+%28PfEMP1%29+pseudogene;size=112;Parent=apidb|PFA0025c;Dbxref=ApiDB_PlasmoDB:PFA0025c,Sanger:PFA0025c,taxon:36329
apidb|MAL1	ApiDB	CDS	53392	53503	.	-	0	ID=apidb|cds_PFA0025c-1;Name=cds;description=.;size=112;Parent=apidb|rna_PFA0025c-1
apidb|MAL1	ApiDB	exon	53392	53503	.	-	.	ID=apidb|exon_PFA0025c-1;Name=exon;description=exon;size=112;Parent=apidb|rna_PFA0025c-1
apidb|MAL1	ApiDB	gene	54001	55229	.	-	.	ID=apidb|PFA0030c;Name=PFA0030c;description=rifin;size=1229;web_id=PFA0030c;locus_tag=PFA0030c;size=1229;Alias=MAL1P4.06
apidb|MAL1	ApiDB	mRNA	54001	55229	.	-	.	ID=apidb|rna_PFA0030c-1;Name=PFA0030c-1;description=rifin;size=1229;Parent=apidb|PFA0030c;Ontology_term=GO:0020033,GO:0016020,GO:0020002,GO:0003674;Dbxref=ApiDB_PlasmoDB:PFA0030c,NCBI_gi:124505653,NCBI_gi:7670010,Sanger:PFA0030c,taxon:36329
apidb|MAL1	ApiDB	CDS	55161	55229	.	-	0	ID=apidb|cds_PFA0030c-1;Name=cds;description=.;size=69;Parent=apidb|rna_PFA0030c-1
apidb|MAL1	ApiDB	CDS	54001	55011	.	-	0	ID=apidb|cds_PFA0030c-1;Name=cds;description=.;size=1011;Parent=apidb|rna_PFA0030c-1
apidb|MAL1	ApiDB	exon	55161	55229	.	-	.	ID=apidb|exon_PFA0030c-1;Name=exon;description=exon;size=69;Parent=apidb|rna_PFA0030c-1
apidb|MAL1	ApiDB	exon	54001	55011	.	-	.	ID=apidb|exon_PFA0030c-2;Name=exon;description=exon;size=1011;Parent=apidb|rna_PFA0030c-1
apidb|MAL1	ApiDB	gene	56913	57116	.	-	.	ID=apidb|PFA0035c;Name=PFA0035c;description=hypothetical+protein%2C+conserved+in+P.+falciparum;size=204;web_id=PFA0035c;locus_tag=PFA0035c;size=204;Alias=MAL1P4.06b
apidb|MAL1	ApiDB	mRNA	56913	57116	.	-	.	ID=apidb|rna_PFA0035c-1;Name=PFA0035c-1;description=hypothetical+protein%2C+conserved+in+P.+falciparum;size=204;Parent=apidb|PFA0035c;Dbxref=ApiDB_PlasmoDB:PFA0035c,NCBI_gi:124505655,NCBI_gi:7670011,Sanger:PFA0035c,taxon:36329
apidb|MAL1	ApiDB	CDS	56913	57116	.	-	0	ID=apidb|cds_PFA0035c-1;Name=cds;description=.;size=204;Parent=apidb|rna_PFA0035c-1
"""
plasmodb_gff3_file = None


def setup_module():
    global plasmodb_gff3_file
    plasmodb_gff3_file = NamedTemporaryFile(delete=False)
    plasmodb_gff3_file.write(plasmodb_gff3)
    plasmodb_gff3_file.close()


def test_fromgff3():
    
    features = fromgff3(plasmodb_gff3_file.name)
    
    expect_header = ('seqid', 'source', 'type', 'start', 'end', 'score', 'strand', 'phase', 'attributes')
    eq_(expect_header, header(features))

    # apidb|MAL1    ApiDB    supercontig    1    643292    .    +    .    ID=apidb|MAL1;Name=MAL1;description=MAL1;size=643292;web_id=MAL1;molecule_type=dsDNA;organism_name=Plasmodium falciparum;translation_table=11;topology=linear;localization=nuclear;Dbxref=ApiDB_PlasmoDB:MAL1,GenBank:NC_004325,taxon:36329
    row = list(features)[1]
    eq_('apidb|MAL1', row[0])
    eq_('ApiDB', row[1])
    eq_('supercontig', row[2])
    eq_(1, row[3])
    eq_(643292, row[4])
    eq_('.', row[5])
    eq_('+', row[6])
    eq_('.', row[7])
    eq_('apidb|MAL1', row[8]['ID']) 
    eq_('MAL1', row[8]['Name'])
    eq_('Plasmodium falciparum', row[8]['organism_name'])
    
    # test data wrapped in hybrid rows
    eq_('apidb|MAL1', row['seqid'])
    eq_('ApiDB', row['source'])
    eq_('supercontig', row['type'])
    eq_(1, row['start'])
    eq_(643292, row['end'])
    eq_('.', row['score'])
    eq_('+', row['strand'])
    eq_('.', row['phase'])
    eq_('apidb|MAL1', row['attributes']['ID']) 
    eq_('MAL1', row['attributes']['Name'])
    eq_('Plasmodium falciparum', row['attributes']['organism_name'])
    
    
def test_fromgff3_trailing_semicolon():
    
    features = fromgff3(plasmodb_gff3_file.name)
    
    #apidb|MAL2    ApiDB    supercontig    1    947102    .    +    .    ID=apidb|MAL2;Name=MAL2;description=MAL2;size=947102;web_id=MAL2;molecule_type=dsDNA;organism_name=Plasmodium falciparum;translation_table=11;topology=linear;localization=nuclear;Dbxref=ApiDB_PlasmoDB:MAL2,GenBank:NC_000910,taxon:36329;
    row = list(features)[2]
    eq_('apidb|MAL2', row[0])
    eq_('ApiDB', row[1])
    eq_('supercontig', row[2])
    eq_(1, row[3])
    eq_(947102, row[4])
    eq_('.', row[5])
    eq_('+', row[6])
    eq_('.', row[7])
    eq_('apidb|MAL2', row[8]['ID']) 
    eq_('MAL2', row[8]['Name'])
    eq_('Plasmodium falciparum', row[8]['organism_name'])
    
    
def test_gff3lookup():
    
    features = fromgff3(plasmodb_gff3_file.name)
    genes = selecteq(features, 'type', 'gene')
    lkp = gff3lookup(genes)
    
    #apidb|MAL1    ApiDB    gene    56913    57116    .    -    .    ID=apidb|PFA0035c;Name=PFA0035c;description=hypothetical+protein%2C+conserved+in+P.+falciparum;size=204;web_id=PFA0035c;locus_tag=PFA0035c;size=204;Alias=MAL1P4.06b

    actual = lkp['apidb|MAL1'][56911:56915]
    eq_(1, len(actual))
    eq_(56913, actual[0][3])
    eq_(57116, actual[0][4])

    actual = lkp['apidb|MAL1'][56915]
    eq_(1, len(actual))
    eq_(56913, actual[0][3])
    eq_(57116, actual[0][4])


def test_gff3join():    

    #apidb|MAL1    ApiDB    gene    56913    57116    .    -    .    ID=apidb|PFA0035c;Name=PFA0035c;description=hypothetical+protein%2C+conserved+in+P.+falciparum;size=204;web_id=PFA0035c;locus_tag=PFA0035c;size=204;Alias=MAL1P4.06b
    snps = (('chr', 'pos'),
            ('apidb|MAL1', 56911),
            ('apidb|MAL1', 56915))
    features = fromgff3(plasmodb_gff3_file.name)
    genes = selecteq(features, 'type', 'gene')
    actual = gff3join(snps, genes, seqid='chr', start='pos', end='pos')
    expect = (('chr', 'pos', 'seqid', 'source', 'type', 'start', 'end', 'score', 'strand', 'phase', 'attributes'),
              ('apidb|MAL1', 56915, 'apidb|MAL1', 'ApiDB', 'gene', 56913, 57116, '.', '-', '.', gff3_parse_attributes("ID=apidb|PFA0035c;Name=PFA0035c;description=hypothetical+protein%2C+conserved+in+P.+falciparum;size=204;web_id=PFA0035c;locus_tag=PFA0035c;size=204;Alias=MAL1P4.06b")))
    ieq(expect, actual)
    ieq(expect, actual)
    
    
def test_gff3leftjoin():    

    #apidb|MAL1    ApiDB    gene    56913    57116    .    -    .    ID=apidb|PFA0035c;Name=PFA0035c;description=hypothetical+protein%2C+conserved+in+P.+falciparum;size=204;web_id=PFA0035c;locus_tag=PFA0035c;size=204;Alias=MAL1P4.06b
    snps = (('chr', 'pos'),
            ('apidb|MAL1', 56911),
            ('apidb|MAL1', 56915))
    features = fromgff3(plasmodb_gff3_file.name)
    genes = selecteq(features, 'type', 'gene')
    actual = gff3leftjoin(snps, genes, seqid='chr', start='pos', end='pos')
    expect = (('chr', 'pos', 'seqid', 'source', 'type', 'start', 'end', 'score', 'strand', 'phase', 'attributes'),
              ('apidb|MAL1', 56911, None, None, None, None, None, None, None, None, None),
              ('apidb|MAL1', 56915, 'apidb|MAL1', 'ApiDB', 'gene', 56913, 57116, '.', '-', '.', gff3_parse_attributes("ID=apidb|PFA0035c;Name=PFA0035c;description=hypothetical+protein%2C+conserved+in+P.+falciparum;size=204;web_id=PFA0035c;locus_tag=PFA0035c;size=204;Alias=MAL1P4.06b")))
    ieq(expect, actual)
    ieq(expect, actual)
    
    
def test_integration():
    #apidb|MAL1    ApiDB    gene    56913    57116    .    -    .    ID=apidb|PFA0035c;Name=PFA0035c;description=hypothetical+protein%2C+conserved+in+P.+falciparum;size=204;web_id=PFA0035c;locus_tag=PFA0035c;size=204;Alias=MAL1P4.06b
    snps = etl.wrap((('chr', 'pos'),
                     ('apidb|MAL1', 56911),
                     ('apidb|MAL1', 56915)))
    features = etl.fromgff3(plasmodb_gff3_file.name)
    genes = features.selecteq('type', 'gene')
    actual = snps.gff3join(genes, seqid='chr', start='pos', end='pos')
    expect = (('chr', 'pos', 'seqid', 'source', 'type', 'start', 'end', 'score', 'strand', 'phase', 'attributes'),
              ('apidb|MAL1', 56915, 'apidb|MAL1', 'ApiDB', 'gene', 56913, 57116, '.', '-', '.', gff3_parse_attributes("ID=apidb|PFA0035c;Name=PFA0035c;description=hypothetical+protein%2C+conserved+in+P.+falciparum;size=204;web_id=PFA0035c;locus_tag=PFA0035c;size=204;Alias=MAL1P4.06b")))
    ieq(expect, actual)
    ieq(expect, actual)
    
    
    
