package org.research.nih.p2;

import java.io.FileOutputStream;
import java.io.IOException;
import java.util.List;
import org.apache.jena.rdf.model.InfModel;
import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.ModelFactory;
import org.apache.jena.rdf.model.Property;
import org.apache.jena.rdf.model.RDFNode;
import org.apache.jena.rdf.model.Statement;
import org.apache.jena.rdf.model.StmtIterator;
import org.apache.jena.reasoner.rulesys.GenericRuleReasoner;
import org.apache.jena.reasoner.rulesys.Rule;
import org.apache.jena.riot.Lang;
import org.apache.jena.riot.RDFDataMgr;

/**
 * Apache Jena full original RO/GenEx/Bgee input, with EXACTLY three
 * authenticated property axioms. This is a different source-rule engine,
 * not independent full OWL RL or source evidence for clinical efficacy.
 */
public final class BgeeThreeRules {
    static final String GENEX="http://purl.org/genex#isExpressedIn";
    static final String EXPRESS="http://purl.obolibrary.org/obo/RO_0002206";
    static final String GENOMIC="http://purl.obolibrary.org/obo/RO_0002330";
    static final String INVERSE="http://purl.obolibrary.org/obo/RO_0002292";
    static final String SUB="http://www.w3.org/2000/01/rdf-schema#subPropertyOf";
    static final String INV="http://www.w3.org/2002/07/owl#inverseOf";
    static final String GENE="http://omabrowser.org/ontology/oma#GENE_";
    static final String ANATOMY="http://purl.obolibrary.org/obo/";
    static final String CONDITION="http://bgee.org/#EXPRESSION_CONDITION_";

    private BgeeThreeRules() {}

    static String rules() {
        return "[authorNamedGeneExpressedIn: (<"+GENEX+"> <"+SUB+"> <"+EXPRESS+">) "+
               "(?gene <"+GENEX+"> ?place) -> (?gene <"+EXPRESS+"> ?place)]\n"+
               "[originalRONamedGenomicParent: (<"+EXPRESS+"> <"+SUB+"> <"+GENOMIC+">) "+
               "(?gene <"+EXPRESS+"> ?place) -> (?gene <"+GENOMIC+"> ?place)]\n"+
               "[originalROInverse: (<"+EXPRESS+"> <"+INV+"> <"+INVERSE+">) "+
               "(?gene <"+EXPRESS+"> ?place) -> (?place <"+INVERSE+"> ?gene)]";
    }

    static boolean target(String uri) {
        return uri.startsWith(ANATOMY) || uri.startsWith(CONDITION);
    }

    static long copy(Model output, InfModel source, String predicate, boolean reverse) {
        long n=0;
        Property p=output.createProperty(predicate);
        StmtIterator it=source.listStatements(null,p,(RDFNode)null);
        try {
            while(it.hasNext()) {
                Statement st=it.nextStatement();
                if(!st.getSubject().isURIResource() || !st.getObject().isURIResource())
                    continue;
                String s=st.getSubject().getURI();
                String o=st.getResource().getURI();
                if (reverse ? target(s)&&o.startsWith(GENE)
                            : s.startsWith(GENE)&&target(o)) {
                    output.add(st);
                    n++;
                }
            }
        } finally {
            it.close();
        }
        return n;
    }

    public static void main(String[] args) throws IOException {
        if(args.length!=2) throw new IllegalArgumentException(
            "Pass only entire authenticated original source N-Triples input and an ephemeral result path");
        Model original=ModelFactory.createDefaultModel();
        RDFDataMgr.read(original,args[0],Lang.NTRIPLES);
        if(original.size()<25027 || original.size()>90000)
            throw new IllegalArgumentException("full source graph size outside original finite bounds");
        if(!original.contains(original.createResource(GENEX),
                              original.createProperty(SUB),
                              original.createResource(EXPRESS)) ||
           !original.contains(original.createResource(EXPRESS),
                              original.createProperty(SUB),
                              original.createResource(GENOMIC)) ||
           !original.contains(original.createResource(EXPRESS),
                              original.createProperty(INV),
                              original.createResource(INVERSE))) {
            throw new IllegalArgumentException("all THREE authentic original source property axioms required");
        }
        List<Rule> rules=Rule.parseRules(rules());
        if(rules.size()!=3) throw new IllegalArgumentException("exact source rule count changed");
        GenericRuleReasoner engine=new GenericRuleReasoner(rules);
        engine.setMode(GenericRuleReasoner.FORWARD_RETE);
        InfModel inferred=ModelFactory.createInfModel(engine,original);
        inferred.prepare();
        Model output=ModelFactory.createDefaultModel();
        copy(output,inferred,EXPRESS,false);
        copy(output,inferred,GENOMIC,false);
        copy(output,inferred,INVERSE,true);
        if(output.size()>100000)
            throw new IllegalArgumentException("original source named inference size bound exceeded");
        try(FileOutputStream file=new FileOutputStream(args[1])) {
            RDFDataMgr.write(file,output,Lang.NTRIPLES);
        }
        System.out.println("JENA_FULL_AUTHENTICATED_ORIGINAL_GRAPH_TRIPLES="+original.size());
        System.out.println("JENA_EXACT_AUTHENTICATED_RULES="+rules.size());
        System.out.println("JENA_COMPLETE_SOURCE_RULE_OUTPUT="+output.size());
        System.out.println("JENA_COMPLETE_OWL_RL_PROFILE=false");
    }
}
