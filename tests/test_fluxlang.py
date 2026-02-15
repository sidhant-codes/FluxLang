"""
test_fluxlang.py  pytest test suite for the FluxLang interpreter.

Each test class maps to one language feature.  Two complementary approaches:
1. Inline source - short snippets written directly in the test.
2. .flux fixture files in tests/flux/ for integration checks.

Run:
    pytest tests/
    pytest tests/ -v
    pytest tests/ -k arithmetic
"""

from __future__ import annotations
import os, sys, pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from helpers import run_flux, run_flux_file
from fluxlang.core.errors import FluxLangError

FLUX_DIR = os.path.join(_HERE, "flux")

def _flux(name):
    return os.path.join(FLUX_DIR, name)


# 01 Hello World
class TestHelloWorld:
    def test_file(self):
        assert run_flux_file(_flux("01_hello_world.flux")) == ["Hello, World!"]
    def test_inline(self):
        assert run_flux('print("Hello, World!");') == ["Hello, World!"]
    def test_multiple_prints(self):
        assert run_flux('print("a"); print("b"); print("c");') == ["a", "b", "c"]


# 02 Variables
class TestVariables:
    def test_file(self):
        assert run_flux_file(_flux("02_variables.flux")) == ["42", "3.14", "FluxLang", "True", "None"]
    def test_int(self):
        assert run_flux("let x = 10; print(x);") == ["10"]
    def test_float(self):
        assert run_flux("let x = 2.5; print(x);") == ["2.5"]
    def test_string(self):
        assert run_flux('let x = "hi"; print(x);') == ["hi"]
    def test_bool_true(self):
        assert run_flux("let x = true; print(x);") == ["True"]
    def test_bool_false(self):
        assert run_flux("let x = false; print(x);") == ["False"]
    def test_null(self):
        assert run_flux("let x = null; print(x);") == ["None"]
    def test_reassignment(self):
        assert run_flux("let x = 1; x = 2; print(x);") == ["2"]
    def test_undefined_variable_raises(self):
        with pytest.raises(FluxLangError, match="Undefined variable"):
            run_flux("print(unknown);")


# 03 Arithmetic
class TestArithmetic:
    def test_file(self):
        assert run_flux_file(_flux("03_arithmetic.flux")) == ["5", "6", "21", "2.5", "3", "1", "256"]
    def test_addition(self):
        assert run_flux("print(2 + 3);") == ["5"]
    def test_subtraction(self):
        assert run_flux("print(10 - 4);") == ["6"]
    def test_multiplication(self):
        assert run_flux("print(3 * 7);") == ["21"]
    def test_true_division(self):
        assert run_flux("print(10 / 4);") == ["2.5"]
    def test_floor_division(self):
        assert run_flux("print(10 // 3);") == ["3"]
    def test_modulo(self):
        assert run_flux("print(10 % 3);") == ["1"]
    def test_power(self):
        assert run_flux("print(2 ** 8);") == ["256"]
    def test_string_concat(self):
        assert run_flux('print("foo" + "bar");') == ["foobar"]
    def test_int_plus_string_coerces(self):
        assert run_flux('print(1 + "x");') == ["1x"]
    def test_division_by_zero(self):
        with pytest.raises(FluxLangError, match="Division by zero"):
            run_flux("print(1 / 0);")
    def test_modulo_by_zero(self):
        with pytest.raises(FluxLangError, match="Modulo by zero"):
            run_flux("print(1 % 0);")
    def test_floor_div_by_zero(self):
        with pytest.raises(FluxLangError, match="Division by zero"):
            run_flux("print(1 // 0);")
    def test_unary_minus(self):
        assert run_flux("print(-5);") == ["-5"]
    def test_negative_arithmetic(self):
        assert run_flux("let x = -3; print(x * -2);") == ["6"]


# 04 If/elif/else
class TestIfElifElse:
    def test_file(self):
        assert run_flux_file(_flux("04_if_elif_else.flux")) == ["Grade: B"]
    def test_if_true(self):
        assert run_flux("if (true) { print(1); }") == ["1"]
    def test_if_false_skipped(self):
        assert run_flux("if (false) { print(1); }") == []
    def test_else_branch(self):
        assert run_flux("if (false) { print(1); } else { print(2); }") == ["2"]
    def test_elif_match(self):
        src = 'let x = 5; if (x > 10) { print("big"); } elif (x > 3) { print("med"); } else { print("sm"); }'
        assert run_flux(src) == ["med"]
    def test_elif_falls_to_else(self):
        src = 'let x = 1; if (x > 10) { print("big"); } elif (x > 3) { print("med"); } else { print("sm"); }'
        assert run_flux(src) == ["sm"]
    def test_nested_if(self):
        src = 'let x = 5; if (x > 0) { if (x > 3) { print("deep"); } }'
        assert run_flux(src) == ["deep"]


# 05 While loop
class TestWhileLoop:
    def test_file(self):
        assert run_flux_file(_flux("05_while_loop.flux")) == ["0", "1", "2", "3", "4"]
    def test_zero_iterations(self):
        assert run_flux("let i = 10; while (i < 0) { print(i); }") == []
    def test_accumulator(self):
        src = "let s = 0; let i = 1; while (i <= 5) { s += i; i += 1; } print(s);"
        assert run_flux(src) == ["15"]


# 06 For loop
class TestForLoop:
    def test_file(self):
        assert run_flux_file(_flux("06_for_loop.flux")) == ["0", "1", "2", "3", "4"]
    def test_sum(self):
        src = "let s = 0; for (let i = 1; i <= 10; i += 1) { s += i; } print(s);"
        assert run_flux(src) == ["55"]
    def test_step_two(self):
        src = "for (let i = 0; i < 10; i += 2) { print(i); }"
        assert run_flux(src) == ["0", "2", "4", "6", "8"]


# 07 For-in loop
class TestForInLoop:
    def test_file(self):
        assert run_flux_file(_flux("07_for_in_loop.flux")) == ["red", "green", "blue"]
    def test_sum_array(self):
        src = "let nums = [1, 2, 3, 4, 5]; let s = 0; for (n in nums) { s += n; } print(s);"
        assert run_flux(src) == ["15"]
    def test_empty_array(self):
        assert run_flux("let a = []; for (x in a) { print(x); }") == []
    def test_non_iterable_raises(self):
        with pytest.raises(FluxLangError, match="requires an array"):
            run_flux('for (x in 42) { print(x); }')
    def test_string_chars(self):
        assert run_flux('for (c in "hi") { print(c); }') == ["h", "i"]
    def test_dict_keys(self):
        src = 'let d = {"a": 1, "b": 2}; for (k in d) { print(k + "=" + d[k]); }'
        assert run_flux(src) == ["a=1", "b=2"]
    def test_dict_modified_in_body(self):
        src = 'let d = {"a": 1}; for (k in d) { d["z"] = 0; } print(len(d));'
        assert run_flux(src) == ["2"]


# 08 Functions
class TestFunctions:
    def test_file(self):
        assert run_flux_file(_flux("08_functions.flux")) == ["7", "Hello, World!"]
    def test_no_return_is_none(self):
        assert run_flux("func f() {} print(f());") == ["None"]
    def test_return_value(self):
        assert run_flux("func sq(x) { return x * x; } print(sq(7));") == ["49"]
    def test_multiple_params(self):
        assert run_flux("func add(a,b,c){ return a+b+c; } print(add(1,2,3));") == ["6"]
    def test_wrong_arity_raises(self):
        with pytest.raises(FluxLangError, match="expects"):
            run_flux("func f(x){} f(1,2);")
    def test_undefined_function_raises(self):
        with pytest.raises(FluxLangError, match="Undefined function"):
            run_flux("nope();")
    def test_function_as_value(self):
        src = "func double(x) { return x * 2; } let d = double; print(d(5));"
        assert run_flux(src) == ["10"]


# 09 Recursion
class TestRecursion:
    def test_file(self):
        assert run_flux_file(_flux("09_recursion.flux")) == ["1", "1", "120", "3628800"]
    def test_fibonacci(self):
        src = "func fib(n) { if (n <= 1) { return n; } return fib(n-1)+fib(n-2); } print(fib(0)); print(fib(1)); print(fib(7));"
        assert run_flux(src) == ["0", "1", "13"]
    def test_stack_overflow_raises(self):
        with pytest.raises((FluxLangError, RecursionError)):
            run_flux("func inf(n) { return inf(n+1); } inf(0);")


# 10 Arrays
class TestArrays:
    def test_file(self):
        assert run_flux_file(_flux("10_arrays.flux")) == ["5", "1", "5", "5", "4"]
    def test_literal(self):
        assert run_flux("let a = [1,2,3]; print(a[1]);") == ["2"]
    def test_negative_index(self):
        assert run_flux("let a = [1,2,3]; print(a[-1]);") == ["3"]
    def test_out_of_range_raises(self):
        with pytest.raises(FluxLangError, match="out of range"):
            run_flux("let a = [1]; print(a[5]);")
    def test_mutation(self):
        assert run_flux("let a = [1,2,3]; a[1] = 99; print(a[1]);") == ["99"]
    def test_push_pop(self):
        src = "let a = []; push(a, 10); push(a, 20); print(pop(a)); print(len(a));"
        assert run_flux(src) == ["20", "1"]
    def test_remove(self):
        src = "let a = [10, 20, 30]; remove(a, 1); print(toString(a));"
        assert run_flux(src) == ["[10, 30]"]
    def test_nested_array(self):
        assert run_flux("let m = [[1,2],[3,4]]; print(m[1][0]);") == ["3"]


# 11 Dictionaries
class TestDicts:
    def test_file(self):
        assert run_flux_file(_flux("11_dicts.flux")) == ["Alice", "30", "NY", "True", "False"]
    def test_literal_and_read(self):
        assert run_flux('let d = {"x": 1}; print(d["x"]);') == ["1"]
    def test_write_new_key(self):
        assert run_flux('let d = {}; d["k"] = 42; print(d["k"]);') == ["42"]
    def test_missing_key_raises(self):
        with pytest.raises(FluxLangError, match="not found"):
            run_flux('let d = {}; print(d["missing"]);')
    def test_has(self):
        src = 'let d = {"a": 1}; print(has(d, "a")); print(has(d, "b"));'
        assert run_flux(src) == ["True", "False"]


# 12 Classes
class TestClasses:
    def test_file(self):
        assert run_flux_file(_flux("12_classes.flux")) == ["Cat says: Meow", "Dog says: Woof"]
    def test_basic_class(self):
        src = """
        class Counter {
            func init(start) { self.count = start; }
            func inc() { self.count += 1; }
            func get() { return self.count; }
        }
        let c = Counter(0); c.inc(); c.inc(); print(c.get());
        """
        assert run_flux(src) == ["2"]
    def test_no_init_no_args(self):
        assert run_flux("class Foo {} let f = Foo(); print(type(f));") == ["Foo"]
    def test_no_init_with_args_raises(self):
        with pytest.raises(FluxLangError):
            run_flux("class Foo {} Foo(1);")
    def test_undefined_method_raises(self):
        with pytest.raises(FluxLangError, match="no method"):
            run_flux("class Foo {} let f = Foo(); f.bar();")
    def test_undefined_attr_raises(self):
        with pytest.raises(FluxLangError, match="no attribute"):
            run_flux("class Foo {} let f = Foo(); print(f.x);")


# 13 Inheritance
class TestInheritance:
    def test_file(self):
        assert run_flux_file(_flux("13_inheritance.flux")) == [
            "Buddy says: Woof!",
            "I am an animal named Buddy",
            '["Sit", "Roll"]',
        ]
    def test_child_inherits_parent_method(self):
        src = """
        class A { func hello() { print("from A"); } }
        class B extends A {}
        let b = B(); b.hello();
        """
        assert run_flux(src) == ["from A"]
    def test_child_overrides_method(self):
        src = """
        class A { func greet() { print("A"); } }
        class B extends A { func greet() { print("B"); } }
        let b = B(); b.greet();
        """
        assert run_flux(src) == ["B"]
    def test_undefined_parent_raises(self):
        with pytest.raises(FluxLangError, match="Undefined parent class"):
            run_flux("class Child extends Ghost {}")


# 14 Try/Catch
class TestTryCatch:
    def test_file(self):
        assert run_flux_file(_flux("14_try_catch.flux")) == ["Caught: something went wrong"]
    def test_catches_user_throw(self):
        assert run_flux('try { throw "oops"; } catch (e) { print(e); }') == ["oops"]
    def test_catches_runtime_error(self):
        assert run_flux('try { let a = []; print(a[5]); } catch (e) { print("err"); }') == ["err"]
    def test_body_runs_if_no_error(self):
        assert run_flux('try { print("ok"); } catch (e) { print("bad"); }') == ["ok"]
    def test_throw_int(self):
        assert run_flux("try { throw 42; } catch (e) { print(toString(e)); }") == ["42"]


# 15 Lambda / Closures
class TestLambdaClosures:
    def test_file(self):
        assert run_flux_file(_flux("15_lambda_closures.flux")) == ["15", "1", "2", "3"]
    def test_simple_lambda(self):
        assert run_flux("let sq = func(x) { return x * x; }; print(sq(6));") == ["36"]
    def test_immediately_invoked(self):
        assert run_flux("print((func(x){ return x+1; })(9));") == ["10"]
    def test_closure_captures_variable(self):
        src = "let base = 100; let add = func(n) { return base + n; }; print(add(5));"
        assert run_flux(src) == ["105"]
    def test_higher_order_function(self):
        src = "func apply(f, x) { return f(x); } let double = func(n) { return n * 2; }; print(apply(double, 7));"
        assert run_flux(src) == ["14"]


# 16 Builtins
class TestBuiltins:
    def test_file(self):
        assert run_flux_file(_flux("16_builtins.flux")) == [
            "42", "3.14", "true", "false", "null",
            "[1, 2, 3]", "123", "3.14",
            "int", "float", "string", "bool", "null", "array", "dict",
        ]
    def test_len_string(self):
        assert run_flux('print(len("hello"));') == ["5"]
    def test_len_array(self):
        assert run_flux("print(len([1,2,3]));") == ["3"]
    def test_len_dict(self):
        assert run_flux('print(len({"a":1,"b":2}));') == ["2"]
    def test_toint_string(self):
        assert run_flux('print(toInt("99"));') == ["99"]
    def test_tofloat_int(self):
        assert run_flux("print(toFloat(3));") == ["3.0"]
    def test_tostring_array(self):
        assert run_flux("print(toString([1,2,3]));") == ["[1, 2, 3]"]
    def test_tostring_dict(self):
        assert run_flux('print(toString({"a": "b"}));') == ['{"a": "b"}']
    def test_type_null(self):
        assert run_flux("print(type(null));") == ["null"]
    def test_hasattr(self):
        src = 'class Pt { func init(x) { self.x = x; } } let p = Pt(1); print(hasAttr(p, "x")); print(hasAttr(p, "y"));'
        assert run_flux(src) == ["True", "False"]


# 17 Augmented assignment
class TestAugAssign:
    def test_file(self):
        assert run_flux_file(_flux("17_aug_assign.flux")) == ["8", "6", "24", "8.0", "4.0", "1.0"]
    def test_plus_eq(self):
        assert run_flux("let x = 1; x += 9; print(x);") == ["10"]
    def test_minus_eq(self):
        assert run_flux("let x = 10; x -= 3; print(x);") == ["7"]
    def test_star_eq(self):
        assert run_flux("let x = 3; x *= 4; print(x);") == ["12"]
    def test_slash_eq(self):
        assert run_flux("let x = 10; x /= 4; print(x);") == ["2.5"]
    def test_floordiv_eq(self):
        assert run_flux("let x = 10; x //= 3; print(x);") == ["3"]
    def test_mod_eq(self):
        assert run_flux("let x = 10; x %= 3; print(x);") == ["1"]
    def test_string_concat_eq(self):
        assert run_flux('let s = "foo"; s += "bar"; print(s);') == ["foobar"]


# 18 Break/Continue
class TestBreakContinue:
    def test_file(self):
        assert run_flux_file(_flux("18_break_continue.flux")) == [
            "0", "1", "2", "3", "4",
            "0", "1", "3", "4",
        ]
    def test_break_while(self):
        src = "let i = 0; while (true) { if (i >= 3) { break; } print(i); i += 1; }"
        assert run_flux(src) == ["0", "1", "2"]
    def test_continue_for(self):
        src = "for (let i = 0; i < 4; i += 1) { if (i == 2) { continue; } print(i); }"
        assert run_flux(src) == ["0", "1", "3"]
    def test_break_for_in(self):
        src = "for (x in [1,2,3,4,5]) { if (x == 3) { break; } print(x); }"
        assert run_flux(src) == ["1", "2"]


# 19 Variadic
class TestVariadic:
    def test_file(self):
        assert run_flux_file(_flux("19_variadic.flux")) == ["6", "100", "0"]
    def test_collects_rest(self):
        src = """
        func first_and_rest(a, ...rest) {
            print(a); print(toString(rest));
        }
        first_and_rest(1, 2, 3, 4);
        """
        assert run_flux(src) == ["1", "[2, 3, 4]"]
    def test_zero_extras(self):
        src = "func f(a, ...rest) { return len(rest); } print(f(99));"
        assert run_flux(src) == ["0"]


# 20 Array utilities
class TestArrayUtils:
    def test_file(self):
        assert run_flux_file(_flux("20_array_utils.flux")) == [
            "[10, 20, 30, 40, 50]", "[5, 4, 3, 2, 1]", "True", "False", "[2, 3, 4]",
        ]
    def test_sort(self):
        assert run_flux("let a = [3,1,2]; sort(a); print(toString(a));") == ["[1, 2, 3]"]
    def test_reverse(self):
        assert run_flux("let a = [1,2,3]; reverse(a); print(toString(a));") == ["[3, 2, 1]"]
    def test_contains_true(self):
        assert run_flux("print(contains([1,2,3], 2));") == ["True"]
    def test_contains_false(self):
        assert run_flux("print(contains([1,2,3], 9));") == ["False"]
    def test_slice(self):
        assert run_flux("let a = [0,1,2,3,4]; print(toString(a[1:4]));") == ["[1, 2, 3]"]
    def test_slice_from_start(self):
        assert run_flux("let a = [0,1,2,3]; print(toString(a[:2]));") == ["[0, 1]"]
    def test_slice_to_end(self):
        assert run_flux("let a = [0,1,2,3]; print(toString(a[2:]));") == ["[2, 3]"]


# 21 Strings
class TestStrings:
    def test_file(self):
        assert run_flux_file(_flux("21_strings.flux")) == ["5", "H", "o", "Hello, World!"]
    def test_string_len(self):
        assert run_flux('print(len("abcde"));') == ["5"]
    def test_string_index(self):
        assert run_flux('print("hello"[1]);') == ["e"]
    def test_string_negative_index(self):
        assert run_flux('print("hello"[-1]);') == ["o"]
    def test_string_concat(self):
        assert run_flux('print("foo" + "bar");') == ["foobar"]
    def test_string_out_of_range_raises(self):
        with pytest.raises(FluxLangError, match="out of range"):
            run_flux('print("hi"[10]);')


# 22 Logical operators
class TestLogicalOps:
    def test_file(self):
        assert run_flux_file(_flux("22_logical_ops.flux")) == [
            "True", "False", "True", "False",
            "False", "True",
            "0", "hi", "hi", "1",
        ]
    def test_and_true(self):
        assert run_flux("print(true and true);") == ["True"]
    def test_and_short_circuit(self):
        assert run_flux('print(0 and "hi");') == ["0"]
    def test_or_short_circuit(self):
        assert run_flux('print(1 or "hi");') == ["1"]
    def test_not_true(self):
        assert run_flux("print(not true);") == ["False"]
    def test_not_zero(self):
        assert run_flux("print(not 0);") == ["True"]
    def test_truthy_empty_string(self):
        assert run_flux('if ("") { print("yes"); } else { print("no"); }') == ["no"]
    def test_truthy_nonempty_string(self):
        assert run_flux('if ("x") { print("yes"); } else { print("no"); }') == ["yes"]
    def test_truthy_null(self):
        assert run_flux('if (null) { print("y"); } else { print("n"); }') == ["n"]


# 23 Try/Catch/Finally
class TestTryCatchFinally:
    def test_file(self):
        assert run_flux_file(_flux("23_try_catch_finally.flux")) == [
            "finally ran", "ok", "caught: 42", "done"
        ]
    def test_finally_runs_no_error(self):
        assert run_flux('try { print("body"); } finally { print("fin"); }') == ["body", "fin"]
    def test_finally_runs_on_error(self):
        src = 'try { throw "x"; } catch (e) { print("caught"); } finally { print("fin"); }'
        assert run_flux(src) == ["caught", "fin"]
    def test_finally_runs_after_return(self):
        src = """
        func f() { try { return 1; } finally { print("fin"); } }
        print(f());
        """
        out = run_flux(src)
        assert "fin" in out


# 24 F-strings
class TestFStrings:
    def test_file(self):
        assert run_flux_file(_flux("24_fstrings.flux")) == [
            "Hello from FluxLang!", "Version: 1", "Pi is approximately 3.14", "Active: true",
        ]
    def test_simple_interpolation(self):
        assert run_flux('let x = 42; print(f"x is {x}");') == ["x is 42"]
    def test_expression_in_fstring(self):
        assert run_flux('let a = 3; let b = 4; print(f"{a} + {b} = {a+b}");') == ["3 + 4 = 7"]
    def test_string_var_in_fstring(self):
        assert run_flux('let name = "World"; print(f"Hello, {name}!");') == ["Hello, World!"]


# 25 Dict ops
class TestDictOps:
    def test_file(self):
        assert run_flux_file(_flux("25_dict_ops.flux")) == [
            '["a", "b", "c"]', "[1, 2, 3]", "False", "True",
        ]
    def test_keys(self):
        src = 'let d = {"z":1,"a":2}; let k = keys(d); sort(k); print(toString(k));'
        assert run_flux(src) == ['["a", "z"]']
    def test_values(self):
        src = 'let d = {"a":10,"b":20}; let v = values(d); sort(v); print(toString(v));'
        assert run_flux(src) == ["[10, 20]"]
    def test_del_removes_key(self):
        src = 'let d = {"a":1,"b":2}; del(d,"a"); print(has(d,"a")); print(has(d,"b"));'
        assert run_flux(src) == ["False", "True"]
    def test_del_missing_key_raises(self):
        with pytest.raises((FluxLangError, Exception)):
            run_flux('let d = {}; del(d, "x");')


# 26 Error handling
class TestErrors:
    def test_lexer_error_bad_char(self):
        from fluxlang.core.errors import LexerError
        with pytest.raises(LexerError):
            run_flux("let x = @;")
    def test_parse_error_missing_semi(self):
        from fluxlang.core.errors import ParseError
        with pytest.raises(ParseError):
            run_flux("let x = 1")
    def test_runtime_error_undefined_var(self):
        from fluxlang.core.errors import FluxLangRuntimeError
        with pytest.raises(FluxLangRuntimeError, match="Undefined variable"):
            run_flux("print(nope);")
    def test_runtime_type_error(self):
        from fluxlang.core.errors import FluxLangRuntimeError
        with pytest.raises(FluxLangRuntimeError):
            run_flux("let x = 5; x[0];")


# 27 Scope
class TestScope:
    def test_block_does_not_leak(self):
        src = "let x = 1; if (true) { let y = 99; } print(x);"
        assert run_flux(src) == ["1"]
    def test_inner_reads_outer(self):
        src = "let outer = 42; func f() { return outer; } print(f());"
        assert run_flux(src) == ["42"]
    def test_function_does_not_pollute_outer(self):
        src = "let x = 1; func f() { let x = 99; } f(); print(x);"
        assert run_flux(src) == ["1"]


# 28 String concatenation uses FluxLang spelling
class TestConcat:
    def test_bool_and_null(self):
        assert run_flux('print("x" + true + null);') == ["xtruenull"]
    def test_aug_assign(self):
        assert run_flux('let s = "a"; s += false; print(s);') == ["afalse"]


# 29 Error reporting
class TestErrorReporting:
    def test_missing_semi_reports_its_own_line(self):
        from fluxlang.core.errors import ParseError
        with pytest.raises(ParseError) as exc:
            run_flux('print(1);\nprint(2)\n')
        assert exc.value.line == 2
    def test_input_at_eof_is_a_flux_error(self, monkeypatch):
        from fluxlang.core.errors import FluxLangRuntimeError
        def _eof(prompt=""):
            raise EOFError
        monkeypatch.setattr("builtins.input", _eof)
        with pytest.raises(FluxLangRuntimeError, match="end of input"):
            run_flux('let x = input("? ");')
    def test_execution_stopped_bypasses_catch(self):
        from fluxlang.core.errors import ExecutionStopped
        from fluxlang.core.lexer import Lexer
        from fluxlang.core.parser import Parser
        from fluxlang.core.interpreter import Interpreter
        def _stop(line, env):
            raise ExecutionStopped()
        src = 'try { let x = 1; } catch (e) { print("swallowed"); }'
        with pytest.raises(ExecutionStopped):
            Interpreter(on_step=_stop, print_fn=lambda *a: None).interpret(Parser(Lexer(src).tokenize()).parse())


# 30 Interpreter internals
class TestInterpreterInternals:
    @staticmethod
    def _parse(src):
        from fluxlang.core.lexer import Lexer
        from fluxlang.core.parser import Parser
        return Parser(Lexer(src).tokenize()).parse()

    def test_caught_error_has_no_kind_prefix(self):
        src = 'let a = []; try { print(a[5]); } catch (e) { print(e); }'
        out = run_flux(src)
        assert out and "out of range" in out[0].lower() and not out[0].startswith("Runtime Error")
    def test_uncaught_error_keeps_kind_prefix(self):
        from fluxlang.core.errors import FluxLangRuntimeError
        with pytest.raises(FluxLangRuntimeError) as exc:
            run_flux("print(nope);")
        assert "Runtime Error: Undefined variable" in str(exc.value)
    def test_visitor_patched_after_init_is_used(self):
        # The IDE's trace view wraps visitors on the instance after construction.
        from fluxlang.core.interpreter import Interpreter
        interp = Interpreter(print_fn=lambda *a: None)
        seen, orig = [], interp._visit_VarDecl
        def traced(node, env):
            seen.append(node.name)
            return orig(node, env)
        interp._visit_VarDecl = traced
        interp.interpret(self._parse("let x = 1; let y = 2;"))
        assert seen == ["x", "y"]
    def test_import_does_not_change_recursion_limit(self):
        import subprocess
        code = ("import sys; before = sys.getrecursionlimit(); "
                "import fluxlang.core.interpreter; print(sys.getrecursionlimit() == before)")
        out = subprocess.run([sys.executable, "-c", code], cwd=_ROOT, capture_output=True, text=True)
        assert out.stdout.strip() == "True", out.stderr
