#!/usr/bin/env python3
"""Independent bisection/finite-difference checks and displayed-iterate checks.
Requires SymPy and mpmath in the verification environment only.
"""
import json
import re
from pathlib import Path
import mpmath as mp
import sympy as sp
mp.mp.dps = 45
x = sp.Symbol("x")
CASES = [['bracket', '2*x**3 - x**2/2 + 4', '-1.2', '-1.1', '-0.176', '0.733'], ['bracket', 'x**2*log(x) - 2*exp(x) + 4', '0.6', '0.7', '0.1718651746632254042952795890049526766794', '-0.2022761374709319089162917456743109342375'], ['bracket', '3*x**2 + 5/x**3', '-1.11', '-1.1', '0.04034309349524835280861577428414535792184', '-0.1265740045078888054094665664913598797896'], ['bracket', '-7*sqrt(x) + 3*x/4 + 9', '2.37', '2.38', '0.001136977161543301835466397797496720487363', '-0.01407403437905874235514637596215106931629'], ['bracket', '(x + 1)**2 + log(x) - 6', '1.3', '1.4', '-0.4476357355325089479645040131190456027958', '0.09647223662121293050459341021699209011148'], ['bracket', '-2*sin(x)*cos(x) + 2*exp(-2*x)', '3.1', '3.2', '0.08714826409008804672735179601793147723943', '-0.1132260903041454204822539804516623793197'], ['bracket', '-2*sin(x)*cos(x) + 2*exp(-2*x)', '3.1425', '3.1435', '0.001913422115140097972246422650543678658444', '-0.00009401840565703123201738393802519607433151'], ['bracket', 'x**3/2 - 2*cos(x)', '1.1', '1.2', '-0.2416922428511547755427401035694322442429', '0.1392844910466528447232532887538479593201'], ['bracket', 'x**3/2 - 2*cos(x)', '1.1645', '1.1655', '-0.000853691507142333765500727088526034607157', '0.003019722717460473504275052795118394066269'], ['bracket', '2**x - (x + 2)**2 + 1', '-0.8', '-0.7', '0.1343491774985175033993134733889637947219', '-0.07442779332754185775030346541612844506193'], ['bracket', '-4*log(x) + sin(2*x)', '1.18', '1.19', '0.04235301185988255144183236969612057737872', '-0.005738244936815709824504700770115625760719'], ['iteration', 'sqrt(4*x + 2)', '5', 4, '4.470942235045520245315323675458517831647'], ['iteration', '(3*x**2 - 1)**(1/3)', '1', 4, '2.094355610117221666170245327250029903519'], ['iteration', 'sqrt(x**3/3 + 1/3)', '1', 4, '0.6603988368486246880073914295872894230056'], ['iteration', '2*sqrt(sin(x))', '1.5', 3, '1.94278832469017927599877766774846567306'], ['bracket', '-x**2/2 + 2*sin(x)', '1.9335', '1.9345', '0.0006708146057715390248512568495779101446497', '-0.001973726820497284692327751014564392294077'], ['iteration', 'sqrt(x**5/5 + 2/5)', '0.5', 3, '0.6503888388865876898573838984804831106437'], ['bracket', 'x**5 - 5*x**2 + 2', '0.6505', '0.6515', '0.00072476521582815625', '-0.00488719728666428125'], ['bracket', 'x**2/2 + exp(x + 4) - 10', '-1.9', '-1.8', '-0.02883008743234992655027258952136871481685', '0.6450134994341209264717771668886640297202'], ['iteration', 'log(10 - x**2/2) - 4', '-3', 3, '-1.921343754314488442835488748102140625834'], ['bracket', 'x**2/2 + exp(x + 4) - 10', '-1.89545', '-1.89535', '-0.0002240046639609705620536947194718131372605', '0.0004068374188681230599942329116525457282594'], ['bracket', '2*x*sin(x)*cos(x) + sin(x)**2', '1.8', '1.9', '0.1518424102363392112550366371461205753219', '-0.2670461368339578938955294764505140384597'], ['iteration', 'acos(-sin(x)/(2*x))', '1.8', 3, '1.836998996028406909389151870329425267154'], ['bracket', '-x + 1/(x + 1)', '0.5', '1', '0.1666666666666666666666666666666666666667', '-0.5'], ['bracket', 'x**2 - 6*x + 7', '1.5', '1.6', '0.25', '-0.04'], ['newton', 'x**2 - 6*x + 7', '1.6', '1.585714285714285714285714285714285714286'], ['bracket', 'x**4 - 3*x**2 + x + 1', '1.2', '1.3', '-0.0464', '0.0861'], ['newton', 'x**4 - 3*x**2 + x + 1', '1.3', '1.256690140845070422535211267605633802817'], ['bracket', '4*cos(x)**2 - exp(-x)', '1.3', '1.4', '0.01369070022809292928226252914624821486566', '-0.1310416452789227821134374745660756579911'], ['newton', '4*cos(x)**2 - exp(-x)', '1.3', '1.30765068537865086240744111801713118673'], ['bracket', '-x**2/4 + 3*x/4 + exp(-x/4)', '3.4', '3.5', '0.08741493194872666992045084117638347300392', '-0.02063798032149159741470281766360765538127'], ['newton', '-x**2/4 + 3*x/4 + exp(-x/4)', '3.5', '3.481309825636804673452127838446652728916'], ['bracket', '-x**2/4 + 3*x/4 + exp(-x/4)', '3.4805', '3.4815', '0.000804121076905632947971524851710767250438', '-0.0002910906294799217957325047668689857503841'], ['bracket', '-log(x)/4 + cos(x)**2/x', '1.2', '1.3', '0.06383889599265905194339456565521179652023', '-0.0105482789510832375464517473530082578987'], ['newton', '-log(x)/4 + cos(x)**2/x', '1.3', '1.283288208823114392190167604154803120024'], ['bracket', 'x + 5 - 4/x**2', '0.8', '0.9', '-0.45', '0.9617283950617283950617283950617283950617'], ['newton', 'x + 5 - 4/x**2', '-5', '-4.829059829059829059829059829059829059829'], ['bracket', '-2*x**3/25 + 21*x**2/10 - 14*x + 17', '8.3', '8.4', '-0.27396', '0.15968'], ['iteration', 'sqrt(4*x**3/105 + 20*x/3 - 170/21)', '8.3', 4, '8.326014727671804297821167243005869620914'], ['bracket', '50*sin(x**2/36)', '10', '11', '17.79209957005327988370203711811857395448', '-10.88798308602270621286619251120811324274'], ['newton', '50*sin(x**2/36)', '10.5', '10.63587084443310538244511167751948351817'], ['bracket', '25*x*cos(x**2/36)/9', '7.515', '7.525', '0.04258657355318123120080809700041244458217', '-0.04468385456802773990953584049151067302437'], ['bracket', 'x/50 - sin(x/3)/9', '5', '5.5', '-0.01060088419464055315643841551396723847695', '0.002696149582500026984205971370089411861925'], ['iteration', '50*sin(x/3)/9', '5.3', 3, '5.414947241257259110390546594532605489455'], ['bracket', '-40*cos(x) + 450*exp(-x/2)', '5', '6', '25.59176196222540724762233664967962119364', '-16.00263070047586648112200487438917673381'], ['newton', '-40*cos(x) + 450*exp(-x/2)', '5', '5.450352283706643927945407050952936798278'], ['bracket', '-4*x**(2/3) + 40*cos(x) + 40', '2', '3', '17.00452233024150662109044826288027936779', '-7.920035156225434748983139086681993641098'], ['iteration', 'acos(x**(2/3)/10 - 1)', '2.5', 4, '2.522959095863581589147038082858240951276'], ['bracket', '-x/2 + cos(x**2)/2 + 1', '1', '1.5', '0.7701511529340698587004683037214883018662', '-0.06408681136136954445669452869820165339441'], ['iteration', 'sqrt(acos(x - 2))', '1.5', 3, '1.459848636590163670926754507513639847543'], ['bracket', '-x + 3*cos(x/3)', '2', '3', '0.3576617823308440021726685531960409600458', '-1.379093082395580847797190177671070188803'], ['iteration', '3*cos(x/3)', '3', 3, '1.96286937149333744991289941398342548988'], ['bracket', '-x + (x - 1)*exp(x)', '1', '2', '-1.0', '5.38905609893065022723042746057500781318'], ['bracket', '-x + (x - 1)*exp(x)', '-0.8065', '-0.8055', '0.00004624901127592506138171685457506098848962', '-0.001313743662558106414296110681829412155788'], ['bracket', '3*x**(4/3) - 4*x/3 - 2', '1.1', '1.2', '-0.06014228566065504126183542413465134795532', '0.2255708490573998377718719997956669826404'], ['newton', '3*x**(4/3) - 4*x/3 - 2', '1.2', '1.122678238058385147235841815696111175689'], ['bracket', '3*x**(4/3) - 4*x/3 - 2', '1.115', '1.125', '-0.01806513741884774801600164132772640764645', '0.01014145140008819326947089110393158944505'], ['bracket', 'exp(-x)*sin(x**2)', '1.5', '2', '0.1736115970288026401750724246991599844536', '-0.1024220800566737176901160761040305712891'], ['newton', 'exp(-x)*sin(x**2)', '1.75', '1.772143693679011674699702320547454264378'], ['bracket', 'exp(-x)*sin(x**2)', '1.7715', '1.7725', '0.0005749301079919052722706954002427168904994', '-0.00002779628773216506427589002778945064601386'], ['newton', '12*x*exp(-2*x) - 1', '1.5', '1.413102628200513844127977931059095087626'], ['iteration', 'asin(x**2/9 + 1/3)', '0.5', 3, '0.3548105928764963789844267150567290079783'], ['newton', 'x**2/3 - 3*sin(x) + 1', '0.4', '0.3539671770272907502211989543793596401485'], ['bracket', '-x + 4*sqrt(x + 2)/5', '1', '2', '0.3856406460551018348219570732046978935542', '-0.4'], ['bracket', '-x/10 + 10*sin(x/3) + 18*exp(-x/2)', '9', '10', '0.711162018287033737938024445245852298357', '-2.784396582771313948687827916898597744592'], ['newton', '-x/10 + 10*sin(x/3) + 18*exp(-x/2)', '9', '9.203191704958626731630634954075985527836'], ['bracket', '-x/10 + 10*sin(x/3) + 18*exp(-x/2)', '9.2025', '9.2035', '0.0007058269793146203688059854453094809454348', '-0.002808732991384691476461920163182676389278'], ['bracket', '3*x**2*log(x) + x**2', '0.7165', '0.7175', '-0.00006730060787478659983708393648449978111169', '0.00208651279687867840735695459661777176328'], ['bracket', '2*x + 10*log(x) - 10', '1.8', '1.9', '-0.5221333509788099181026885938113623023062', '0.2185388617239477599103597720348932963628']]
rows = json.loads((Path(__file__).resolve().parents[1] / "resources/practice-solutions/pure-year-2/chapter-10.json").read_text())["solutions"]
iterations = [step for row in rows for step in row["steps"] if step.get("explanation", "").startswith("Substitute each unrounded iterate")]
newtons = [step for row in rows for step in row["steps"] if step.get("explanation", "").startswith("Use the Newton–Raphson step")]
checks = 0
iteration_index = newton_index = 0
def check(condition, label):
    global checks
    assert condition, label
    checks += 1
def displayed_close(actual, displayed):
    digits = len(displayed.split(".")[1]) if "." in displayed else 0
    return abs(actual - mp.mpf(displayed)) <= mp.mpf("0.50001") * mp.power(10, -digits)
for case in CASES:
    kind, expression, start, *rest = case
    f = sp.lambdify(x, sp.sympify(expression), "mpmath")
    a = mp.mpf(start)
    if kind == "bracket":
        b = mp.mpf(rest[0]); fa, fb = f(a), f(b)
        check(fa * fb < 0, ("endpoint signs", expression, a, b))
        original_a, original_b = a, b
        for _ in range(110):
            mid = (a+b)/2; fm = f(mid)
            if fa*fm <= 0: b = mid
            else: a, fa = mid, fm
        root = (a+b)/2
        check(original_a < root < original_b and abs(f(root)) < mp.mpf("1e-25"), ("independent bisection", expression))
    elif kind == "iteration":
        count = rest[0]
        step = iterations[iteration_index]; iteration_index += 1
        shown = re.findall(r"\\approx(-?\d+(?:\.\d+)?)", step["latex"])
        check(len(shown) == count, "displayed iteration count")
        for displayed in shown:
            a = f(a)
            check(displayed_close(a, displayed), ("actual displayed iterate", expression, displayed))
    elif kind == "newton":
        h = mp.mpf("1e-12")
        numerical_derivative = (f(a+h)-f(a-h))/(2*h)
        result = a - f(a)/numerical_derivative
        step = newtons[newton_index]; newton_index += 1
        displayed = re.findall(r"\\approx(-?\d+(?:\.\d+)?)", step["latex"])[-1]
        check(displayed_close(result, displayed), ("displayed Newton result from finite difference", expression, displayed))
        check(abs(result-mp.mpf(rest[0])) < mp.mpf("1e-20"), "finite difference agrees with symbolic derivative step")
check(iteration_index == len(iterations), "all authored iteration rows checked")
check(newton_index == len(newtons), "all authored Newton rows checked")
# Independent checks of the source corrections, fixed-point claims and domains.
f = lambda z: mp.power(2,z)+1-(z+2)**2
for a,b in [(-4,-3),(-.8,-.7),(5,6)]:
    check(f(a)*f(b)<0, "three disjoint root brackets")
for a in [-20,-3,0,6,20]:
    check(mp.log(2)**3*mp.power(2,a)>0, "positive third derivative")
for root in [4-sp.sqrt(13), 4+sp.sqrt(13)]:
    check(sp.simplify((root**2+3)/8-root)==0, "correct rearrangement")
    check(sp.simplify((root**2-3)/8-root)==-sp.Rational(3,4), "printed incorrect rearrangement")
check(2-mp.sqrt(6)<0, "positive square-root iteration excludes other root")
check(sp.limit(x**3*sp.log(x), x, 0, dir="+")==0, "origin is continuous extension only")
for g,lo,hi,bound in [(lambda z:1/(z+1),mp.mpf(1)/3,mp.mpf(3)/4,mp.mpf(9)/16),(lambda z:3*mp.cos(z/3),mp.mpf("1.6"),mp.mpf(3),mp.sin(1)),(lambda z:(z-1)*mp.exp(z),mp.mpf(-1),mp.mpf(0),1/mp.e),(lambda z:mp.mpf(".8")*mp.sqrt(z+2),mp.mpf(1),mp.mpf(2),mp.mpf(2)/(5*mp.sqrt(3)))]:
    check(lo <= g(lo) <= hi and lo <= g(hi) <= hi, "invariant interval endpoints")
    check(bound<1, "strict contraction bound")
check(abs(mp.sqrt(mp.pi)*6-mp.mpf("10.64")) < mp.mpf(".01"), "first ground crossing")
check(displayed_close(mp.sqrt(mp.pi/2)*6,"7.52"), "first maximum time")
print(json.dumps({"checksPassed":checks,"checksPerformed":checks,"numericalCases":len(CASES),"iterationRows":iteration_index,"newtonRows":newton_index}))
