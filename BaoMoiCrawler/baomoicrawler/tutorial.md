
[Fine tune 1](https://flyyufelix.github.io/2016/10/03/fine-tuning-in-keras-part1.html)
[Fine tune 2](https://flyyufelix.github.io/2016/10/08/fine-tuning-in-keras-part2.html)

**Fine-tuning Techniques**
Below are some general guidelines for fine-tuning implementation:

1. The common practice is to **_truncate_ the last layer** (softmax layer) of the pre-trained network and replace it with our new softmax layer that are relevant to our own problem. For example, pre-trained network on ImageNet comes with a softmax layer with 1000 categories.

If our task is a classification on 10 categories, the new softmax layer of the network will be of 10 categories instead of 1000 categories. We then run back propagation on the network to fine-tune the pre-trained weights. Make sure cross validation is performed so that the network will be able to generalize well.

2.**Use a smaller learning rate** to train the network. Since we expect the pre-trained weights to be quite good already as compared to randomly initialized weights, we do not want to distort them too quickly and too much. A common practice is to make the initial learning rate 10 times smaller than the one used for scratch training.

3. It is also a common practice to **freeze the weights of the first few layers of the pre-trained network**. This is because the first few layers capture universal features like curves and edges that are also relevant to our new problem. We want to keep those weights intact. Instead, we will get the network to focus on learning dataset-specific features in the subsequent layers.


#header one
##header two
###header three

**bold**
_italic_
*italic*
[Visti this Link](google.com)
![image](https://octodex.github.com/images/bannekat.png)

>"block quote"

* item

###Paragraph
Do I contradict myself?.
Very well then I contradict myself,
I am large, I contain multitudes


First Header|Second Header
---------|---------
Content from cell 1 | Content from cell 2
Content in the first column | Content in the second column


- [x] @mentions, #refs, [links](), **formatting**, and <del>tags</del> supported
- [x] list syntax required (any unordered or ordered list supported)
- [x] this is a complete item
- [ ] this is an incomplete item

<b>html tag</b>