quick solution to the instagram engineering challenge to unshred an image

# How it works
using recursivity :
- Pre-compute a matching score between every pair of shreds : the score is computed by counting the number of matching pixels along the edge. Two pixels are considered a match if the difference of their intensity is less than a defined threshold. This technique avoids errors when some shreds are about the same intensity yet not matching at all and some others match yet, have a complete different intensity for some regions.

- For all the remaining shreds, pick the best two matching shreds, assemble them to create a new, larger one and put this new shred back to the remain shreds.

- Done when there's only one shred  remaining