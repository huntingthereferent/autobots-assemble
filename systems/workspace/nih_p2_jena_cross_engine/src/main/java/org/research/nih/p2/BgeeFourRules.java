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
 * Apache Jena full original RO/GenEx/Bgee input, with EXACTLY four
 * authenticated property axioms. This is a different source-rule engine,
 * not independent full OWL RL or source evidence for clinical efficacy.
 */
public final class BgeeFourRules {
    static final String GENEX="http://purl.org/genex#isExpressedIn";
    static final String EXPRESS="http://purl.obolibrary.org/obo/RO_0002206";
    static final String GENOMIC="http://purl.obolibrary.org/obo/RO_0002330";
    static final String INVERSE="http://purl.obolibrary.org/obo/RO_0002292";
    static final String SUB="http://www.w3.org/2000/01/rdf-schema#subPropertyOf";
    static final String INV="http://www.w3.org/2002/07/owl#inverseOf";
    static final String GENE="http://omabrowser.org/ontology/oma#GENE_";
    static final String ANATOMY="http://purl.obolibrary.org/obo/";
    static final String CONDITION="http://bgee.org/#EXPRESSION_CONDITION_";

    private BgeeFourRules() {}

    static String rules() {
        return "[authorNamedGeneExpressedIn: (<"+GENEX+"> <"+SUB+"> <"+EXPRESS+">) "+
               "(?gene <"+GENEX+"> ?place) -> (?gene <"+EXPRESS+"> ?place)]\n"+
               "[originalRONamedGenomicParent: (<"+EXPRESS+"> <"+SUB+"> <"+GENOMIC+">) "+
               "(?gene <"+EXPRESS+"> ?place) -> (?gene <"+GENOMIC+"> ?place)]\n"+
               "[originalROInverse: (<"+EXPRESS+"> <"+INV+"> <"+INVERSE+">) "+
               "(?gene <"+EXPRESS+"> ?place) -> (?place <"+INVERSE+"> ?gene)]\n"+
               "[originalROInverseNamedGenomicParent: (<"+INVERSE+"> <"+SUB+"> <"+GENOMIC+">) "+
               "(?place <"+INVERSE+"> ?gene) -> (?place <"+GENOMIC+"> ?gene)]";
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
        if(args.length!=2 && args.length!=4) throw new IllegalArgumentException(
            "Pass authenticated original N-Triples input, ephemeral result path and optional one-premise ablation");
        String mode=args.length==3 ? args[2] : "full";
        if(!mode.equals("full") && !mode.equals("omit-genex") &&
           !mode.equals("omit-genomic") && !mode.equals("omit-inverse") &&
           !mode.equals("omit-inverse-genomic"))
            throw new IllegalArgumentException("unrecognized single-premise source ablation");
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
                              original.createResource(INVERSE)) ||
           !original.contains(original.createResource(INVERSE),
                              original.createProperty(SUB),
                              original.createResource(GENOMIC))) {
            throw new IllegalArgumentException("all FOUR authentic original source property axioms required");
        }
        // Remove one original owner axiom only from the in-memory model.
        // Every control starts from a newly parsed, unmodified source file.
        if(mode.equals("omit-genex")) {
            original.remove(original.createResource(GENEX),original.createProperty(SUB),
                            original.createResource(EXPRESS));
        } else if(mode.equals("omit-genomic")) {
            original.remove(original.createResource(EXPRESS),original.createProperty(SUB),
                            original.createResource(GENOMIC));
        } else if(mode.equals("omit-inverse")) {
            original.remove(original.createResource(EXPRESS),original.createProperty(INV),
                            original.createResource(INVERSE));
        } else if(mode.equals("omit-inverse-genomic")) {
            original.remove(original.createResource(INVERSE),original.createProperty(SUB),
                            original.createResource(GENOMIC));
        }
        List<Rule> rules=Rule.parseRules(rules());
        if(rules.size()!=4) throw new IllegalArgumentException("exact source rule count changed");
        GenericRuleReasoner engine=new GenericRuleReasoner(rules);
        engine.setMode(GenericRuleReasoner.FORWARD_RETE);
        InfModel inferred=ModelFactory.createInfModel(engine,original);
        inferred.prepare();
        Model output=ModelFactory.createDefaultModel();
        copy(output,inferred,EXPRESS,false);
        copy(output,inferred,GENOMIC,false);
        copy(output,inferred,INVERSE,true);
        copy(output,inferred,GENOMIC,true);
        if(output.size()>125000)
            throw new IllegalArgumentException("original source named inference size bound exceeded");
        try(FileOutputStream file=new FileOutputStream(args[1])) {
            RDFDataMgr.write(file,output,Lang.NTRIPLES);
        }
        System.out.println("JENA_IN_MEMORY_ABLATION_MODE="+mode);
        System.out.println("JENA_WHOLE_ORIGINAL_INPUT_AFTER_IN_MEMORY_ABLATION="+original.size());
        System.out.println("JENA_EXACT_AUTHENTICATED_RULES="+rules.size());
        System.out.println("JENA_COMPLETE_SOURCE_RULE_OUTPUT="+output.size());
        System.out.println("JENA_COMPLETE_OWL_RL_PROFILE=false");
    }
}
