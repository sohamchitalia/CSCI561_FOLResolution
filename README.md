# CSCI561_FOLResolution

## Project Description

RipeApe  pharmacy  is  developing  a  self-service  automated  system  to  alert  customers  about potential drug interactions for both prescription and over-the-counter drugs. Many medications should not be taken together or should not be taken if a patient has certain symptoms and allergies. Evaluating all the criteria for whether a patient can take a particular medication requires the patient's medical history and expert knowledge from a health care provider. The system, however, can provide an instant guideline to keep patients informed and minimize the risk.  
You are assigned by RipeApe to develop a beta version of the system using the first order logic inference. Patient history and drug compatibility data will be encoded as first order logic clauses in  the  knowledge  base.  The  program  takes  a  query  of  new  drug  list  and  provide  a  logical conclusion whether to issue a warning.

![resolution tree](https://i.stack.imgur.com/38EtM.png)
### Input format

Format for input.txt  
[N = NUMBER OF QUERIES]   
[QUERY 1]   
.....    
[QUERY N]    
[K = NUMBER OF GIVEN SENTENCES IN THE KNOWLEDGE BASE]    
[SENTENCE 1]  
.....  
[SENTENCE K]  
  
The first line contains an integer N specifying the number of queries.  
The following N lines contain one query per line.  
The line after the last query contains an integer K specifying the number of sentences in the knowledge base.  
The remaining K lines contain the sentences in the knowledge base, one sentence per line.       
#### Query format
Each query will be a single literal of the form Predicate(Constant_Arguments) or ~Predicate(Constant_Arguments) and will not contain any variables.  
Each predicate will have between 1 and 25 constant arguments. Two or more arguments will be separated by comma.  
  
#### KB format
Each sentence in the knowledge base is written in one of the following forms:  
1)An implication of the form p1∧p2∧... ∧pm⇒q, where its premise is a conjunction of literals and its conclusion is a single literal. Remember that a literal is an atomic sentence or a negated atomic sentence.  
2)A single literal: q or ~q



### Output format
For each query, determine if that query can be inferred from the knowledge base or not, one query per line:  
[ANSWER 1]  
.....  
[ANSWER N]  
Each answer should be either TRUE if you can prove that the corresponding query sentence is true given the knowledge base, or FALSE if you can't.  

**Example 1**  
For this input.txt:  
1  
Take(Alice,NSAIDs)  
2  
Take(x,Warfarin) => ~Take(x,NSAIDs)  
Take(Alice,Warfarin)
  
    
output.txt will be:  
FALSE

## Resolution: Proof by Contradiction
The idea of resolution is simple: if we know that  

p is true or q is true  
and we also know that p is false or r is true  
then it must be the case that q is true or r is true.
  
This line of reasoning is formalized in the Resolution Tautology:    

      (p OR q) AND (NOT p OR r) -> q OR r  
  
In order to apply resolution in a proof:  

We express our hypotheses and conclusion as a product of sums (conjunctive normal form), such as those that appear in the Resolution Tautology. Each maxterm in the CNF of the hypothesis becomes a clause in the proof. We apply the resolution tautology to pairs of clauses, producing new clauses. If we produce all the clauses of the conclusion, we have proven it.  

