package org.research.nih.p2;

import java.io.FileOutputStream;
import java.io.IOException;
import java.util.ArrayList;
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
 * Independent Apache Jena over the *entire* combined, authenticated
 * original Bgee + GenEx + RO input graph. Two author-source-owned rule
 * patterns, not a full general OWL RL/OWL DL model or clinical benchmark.
 *
 * Read-only input: original N-Triples temporary file made by Python author
 * hash gate. Writes only two target predicate consequence sets as ephemeral
 * N-Triples for an independent complete original-input SPARQL comparator.
 */
public final class BgeeCrossEngine {
    private static final String GENEX = "http://purl.org/genex#isExpressedIn";
    private static final String RO_EXPRESSION = "http://purl.obolibrary.org/obo/RO_0002206";
    private static final String RO_EXPRESSES = "http://purl.obolibrary.org/obo/RO_0002292";
    private static final String SUB = "http://www.w3.org/2000/01/rdf-schema#subPropertyOf";
    private static final String INVERSE = "http://www.w3.org/2002/07/owl#inverseOf";
    private static final String GENE = "http://omabrowser.org/ontology/oma#GENE_";
    private static final String ANATOMY = "http://purl.obolibrary.org/obo/";
    private static final String CONDITION = "http://bgee.org/#EXPRESSION_CONDITION_";
    private static final int MAX_INPUT = 90000;
    private static final int MAX_OUTPUT = 100000;

    private BgeeCrossEngine() { }

    static String sourceRuleDefinitions() {
        // Property semantics are *premises read from the independent source
        // ontology*, not assumed from the spelling or ID of a relation.
        return "[sourceOwnerSubproperty: " +
            "(<" + GENEX + "> <" + SUB + "> <" + RO_EXPRESSION + ">) " +
            "(?gene <" + GENEX + "> ?place) " +
            "-> (?gene <" + RO_EXPRESSION + "> ?place)]\n" +
            "[sourceOwnerInverse: " +
            "(<" + RO_EXPRESSION + "> <" + INVERSE + "> <" + RO_EXPRESSES + ">) " +
            "(?gene <" + RO_EXPRESSION + "> ?place) " +
            "-> (?place <" + RO_EXPRESSES + "> ?gene)]";
    }

    static boolean isOriginalMappedTarget(String id) {
        return id.startsWith(ANATOMY) || id.startsWith(CONDITION);
    }

    static void admitTarget(Model results, Statement statement,
                            boolean forward) {
        if (!statement.getSubject().isURIResource()
                || !statement.getObject().isURIResource()) {
            return;
        }
        String subject=statement.getSubject().getURI();
        String object=statement.getResource().getURI();
        boolean sourceNamed = forward
            ? subject.startsWith(GENE) && isOriginalMappedTarget(object)
            : isOriginalMappedTarget(subject) && object.startsWith(GENE);
        if (sourceNamed) {
            results.add(statement);
        }
    }

    public static void main(String[] args) throws IOException {
        if (args.length != 2 && args.length != 3) {
            throw new IllegalArgumentException(
                "Usage: BgeeCrossEngine <whole-authenticated-original.nt> <target-rule-output.nt> [full|omit-subproperty|omit-inverse]");
        }
        String mode = args.length == 3 ? args[2] : "full";
        if (!mode.equals("full") && !mode.equals("omit-subproperty") && !mode.equals("omit-inverse")) {
            throw new IllegalArgumentException("only predeclared original premise-ablation modes permitted");
        }
        Model complete=ModelFactory.createDefaultModel();
        RDFDataMgr.read(complete,args[0],Lang.NTRIPLES);
        if (complete.size() < 25027 || complete.size() > MAX_INPUT) {
            throw new IllegalArgumentException("original entire input graph size outside bound");
        }
        // Apply only the declared ablations to an in-memory copy of the
        // authenticated original graph. Original downloaded files remain intact.
        if (mode.equals("omit-subproperty")) {
            boolean present = complete.contains(complete.createResource(GENEX),
                                                complete.createProperty(SUB),
                                                complete.createResource(RO_EXPRESSION));
            if (!present) throw new IllegalArgumentException("original source premise already absent");
            complete.remove(complete.createResource(GENEX),
                            complete.createProperty(SUB),
                            complete.createResource(RO_EXPRESSION));
        }
        if (mode.equals("omit-inverse")) {
            boolean present = complete.contains(complete.createResource(RO_EXPRESSION),
                                                complete.createProperty(INVERSE),
                                                complete.createResource(RO_EXPRESSES));
            if (!present) throw new IllegalArgumentException("original inverse premise already absent");
            complete.remove(complete.createResource(RO_EXPRESSION),
                            complete.createProperty(INVERSE),
                            complete.createResource(RO_EXPRESSES));
        }
        List<Rule> sourceRules=Rule.parseRules(sourceRuleDefinitions());
        if (sourceRules.size()!=2) {
            throw new IllegalArgumentException("exact two independent owner-source rule constraints required");
        }
        GenericRuleReasoner reasoner=new GenericRuleReasoner(sourceRules);
        reasoner.setMode(GenericRuleReasoner.FORWARD_RETE);
        InfModel reasoned=ModelFactory.createInfModel(reasoner, complete);
        reasoned.prepare();
        Model target=ModelFactory.createDefaultModel();
        Property forward=target.createProperty(RO_EXPRESSION);
        Property inverse=target.createProperty(RO_EXPRESSES);
        StmtIterator statements=reasoned.listStatements(null,forward,(RDFNode)null);
        try {
            while (statements.hasNext()) {
                admitTarget(target,statements.nextStatement(),true);
            }
        } finally {
            statements.close();
        }
        statements=reasoned.listStatements(null,inverse,(RDFNode)null);
        try {
            while (statements.hasNext()) {
                admitTarget(target,statements.nextStatement(),false);
            }
        } finally {
            statements.close();
        }
        if (target.size()>MAX_OUTPUT) {
            throw new IllegalArgumentException("alternative rule engine output exceeded finite size bound");
        }
        try (FileOutputStream output=new FileOutputStream(args[1])) {
            RDFDataMgr.write(output,target,Lang.NTRIPLES);
        }
        System.out.println("JENA_ABLATION_MODE="+mode);
        System.out.println("JENA_IN_MEMORY_GRAPH_AFTER_DECLARED_ABLATION_TRIPLES="+complete.size());
        System.out.println("JENA_OWNED_RULES="+sourceRules.size());
        System.out.println("JENA_TARGET_INFERENCE_TRIPLES="+target.size());
        System.out.println("JENA_FULL_GENERAL_OWL_RL=false");
    }
}
