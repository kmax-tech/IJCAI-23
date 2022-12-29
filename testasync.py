import asyncio
import TelegramBot as tg
import ADFCalc as ADF
import random

async def eternity2():
    x = random.randint(1, 100000000)
    while x != 2:
        x = random.randint(1, 100000000)
    return 1


async def eternity():
    # Sleep for one hou
    await asyncio.sleep(5.0)
    return ('yay!')

async def main():
    # Wait for at most 1 second
    try:
        await asyncio.wait_for(eternity2(), timeout=0.1)
        #print(b)
        print("Inttime")
        return 1
    except asyncio.TimeoutError:
        print('timeout!')
        return 0

asyncio.run(main())

class a():
    def run(self):
        def helperfunc(testinstance, semantics, calcStyle):
            ADF.optimizer = calcStyle
            x = ADF.ControlAndPrint(testinstance, semantics)
            # def part():
            return x.interpretationEvaluator()
            # return part

a().run()

# in order to calculate an ADF first the ControlAndPrint class has to be created with the desired arguments; second the interevaluator method needs to be called
# the helperfunc function transforms this procedure into a function, which does not need any arguments, therefore the function can be called directly by timeit
def helperfunc(testinstance, semantics, calcStyle):
    ADF.optimizer = calcStyle
    x = ADF.ControlAndPrint(testinstance, semantics)
    #def part():
    return x.interpretationEvaluator()
    #return part

nodes = [["j","s;(m,#w)"],["s","s"],["m","!"],["w","?"]]
semantics= ["a", "c", "p"]

# Expected output:
#
#     timeout!