
import re

content = """
## Exam AWS Certified Solutions Architect - Associate SAA-C03 topic 1 question 935 discussion

Exam question from

Amazon's
AWS Certified Solutions Architect - Associate SAA-C03

Question #: 935
Topic #: 1

[All AWS Certified Solutions Architect - Associate SAA-C03 Questions]

A software company needs to upgrade a critical web application. The application currently runs on a single Amazon EC2 instance that the company hosts in a public subnet. The EC2 instance runs a MySQL database. The application's DNS records are published in an Amazon Route 53 zone.A solutions architect must reconfigure the application to be scalable and highly available. The solutions architect must also reduce MySQL read latency.Which combination of solutions will meet these requirements? (Choose two.) 
Suggested Answer: BC 🗳️ 

A. Launch a second EC2 instance in a second AWS Region. Use a Route 53 failover routing policy to redirect the traffic to the second EC2 instance.

B. Create and configure an Auto Scaling group to launch private EC2 instances in multiple Availability Zones. Add the instances to a target group behind a new Application Load Balancer.

C. Migrate the database to an Amazon Aurora MySQL cluster. Create the primary DB instance and reader DB instance in separate Availability Zones.

D. Create and configure an Auto Scaling group to launch private EC2 instances in multiple AWS Regions. Add the instances to a target group behind a new Application Load Balancer.

E. Migrate the database to an Amazon Aurora MySQL cluster with cross-Region read replicas.

**Answer: BC**

**Timestamp: Aug. 3, 2024, 10:53 a.m.**

[View on ExamTopics](https://www.examtopics.com/discussions/amazon/view/144933-exam-aws-certified-solutions-architect-associate-saa-c03/)
"""

answer_match = re.search(r'\*\*Answer:\s+([A-Z]+)\*\*', content)
print(f"Matched Answer: '{answer_match.group(1)}'" if answer_match else "No match")

# Check regex for options
q_text = "Which combination of solutions will meet these requirements? (Choose two.)"
is_multi = "(Choose two" in q_text or "(Choose three" in q_text
print(f"Is Multi: {is_multi}")
