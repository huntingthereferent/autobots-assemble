# Analyze the observed Level-5 public trajectories for minimal predictive history.
seqs={
0:[
('4d05e51626ea','8dfb16618370'),('8dfb16618370','61ecd26f48f6'),('61ecd26f48f6','a9bd5d03cc26'),('a9bd5d03cc26','c84a5e6fcc5e'),('0de2f6eb7460','8bfd417ca711'),('8bfd417ca711','c55059ee42d4'),('c55059ee42d4','f540c3aa6488'),('f540c3aa6488','748f8bfc8dd2'),('748f8bfc8dd2','290e41e7246a'),('290e41e7246a','c785f27b0ec2'),('c785f27b0ec2','7e921076b047'),('b8e5aebd8004','1b8305baa319'),('1b8305baa319','b8e5aebd8004'),('b8e5aebd8004','d00943ccf2e2'),('d00943ccf2e2','75ee277e936d')],
1:[
('464cb59107ef','8b1ab739930d'),('8b1ab739930d','96fe4efa9ee2'),('96fe4efa9ee2','b67b84abe6fd'),('b67b84abe6fd','016fbe1062a7'),('b69a377e3889','683840f89507'),('683840f89507','b4d2cd9fc26e'),('b4d2cd9fc26e','d1b118aff9ce'),('d1b118aff9ce','d4441345ffa4'),('d4441345ffa4','d23242fcf795'),('d23242fcf795','09543c50b04e'),('09543c50b04e','4317f0c04a79'),('96d3b206aa03','01cc0f4c4526'),('01cc0f4c4526','706c644318d9'),('706c644318d9','72bf9ebeb93b'),('72bf9ebeb93b','26bd937b6f73')],
2:[
('33bdcc7ce42b','f8d50ba0ca11'),('f8d50ba0ca11','d2f4ce39e1ed'),('d2f4ce39e1ed','b4874cc1a088'),('b4874cc1a088','951482a4c314'),('11d45a80a545','52fb92a1851d'),('52fb92a1851d','d80b5640c485'),('d80b5640c485','7d0a40af7dfd'),('7d0a40af7dfd','eaa437829225'),('eaa437829225','0a3e4bf0cad1'),('0a3e4bf0cad1','2a6e48cc22b8'),('2a6e48cc22b8','f27ddaa8f9ac'),('a1c8c05517f8','75ecc874301a'),('75ecc874301a','2f443bd7c2d0'),('2f443bd7c2d0','43d5e8d3093f'),('43d5e8d3093f','a15599387780')],
3:[
('0f38ee4784e1','4b62d150ca59'),('4b62d150ca59','21bb04f3c2cc'),('21bb04f3c2cc','66d647747313'),('66d647747313','6b302ce85dfd'),('b01246deec26','79b4fa833478'),('79b4fa833478','ea99da71de24'),('ea99da71de24','e36b5faf557e'),('e36b5faf557e','1daf02c521e4'),('1daf02c521e4','e2beee63308b'),('e2beee63308b','7e0d0e70e0e2'),('7e0d0e70e0e2','eb08734b0381'),('28f6f0d0d124','46c378cb3628'),('46c378cb3628','3dc749aafa3e'),('3dc749aafa3e','99eeaf878fd2'),('99eeaf878fd2','e95bed701785')]
}

from collections import defaultdict
for L in range(0,5):
 table=defaultdict(set);examples=defaultdict(list)
 for obj,seq in seqs.items():
  obs=[x[0] for x in seq]
  for t,(cur,nxt) in enumerate(seq):
   hist=tuple(obs[max(0,t-L):t]) if L else ()
   key=(obj,hist,cur)
   table[key].add(nxt);examples[key].append((t,nxt))
 bad={k:v for k,v in table.items() if len(v)>1}
 print("HISTORY",L,"AMBIG",len(bad))
 for k,v in list(bad.items())[:5]:print(" ",k,v,examples[k])
 if not bad:
  print("MIN_PREDICTIVE_HISTORY",L)
  break

# Explicit witness at L=0 and split at L=1.
seq=seqs[0];obs=[x[0] for x in seq]
for t,(cur,nxt) in enumerate(seq):
 if cur=='b8e5aebd8004':
  print("WITNESS",t,"PREV",obs[t-1] if t else None,"CUR",cur,"NEXT",nxt)
