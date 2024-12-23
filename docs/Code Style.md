# 代码规范

本文档给出了 PyLabelRoboMaster 代码的编码规范。本文档参考 [PEP 8](https://legacy.python.org/dev/peps/pep-0008/)，但对其中的一些标准做出了修改，若和 [PEP 8](https://legacy.python.org/dev/peps/pep-0008/) 规范冲突，请以本文档为准。



## 代码外观

### 缩进

每一级缩进占 4 个空格。



**函数的参数列表缩进**

当函数的参数列表过长，需要换行时，选择下面的缩进方式

**yes**

```python
foo = long_function_name(var_one, var_two,
                         var_three, var_four)

def long_function_name(
    var_one, var_two, var_three,
    var_four
):
    print(var_one)

foo = long_function_name(
    var_one, var_two,
    var_three, var_four
)
```

**no**

```python
foo = long_function_name(var_one, var_two,
                         var_three, var_four
)

def long_function_name(
    var_one, var_two, var_three,
    var_four):
    print(var_one)

foo = long_function_name(
    var_one, var_two,
    var_three, var_four)
```



**`if` 语句缩进**

`if` 中的条件过长时，选择下面的方式缩进，换行应使用显示的换行符 `\` 分割

```python
if (this_is_one_thing and \
    that_is_another_thing):
    do_something()
```



**数组缩进**

如果列表或参数列表中的数据格式为数组，应选择下面的缩进格式

```python
my_list = [
    1, 2, 3,
    4, 5, 6,
]

result = some_function_that_takes_arguments(
    'a', 'b', 'c',
    'd', 'e', 'f',
)
```



**运算缩进**

当一个包含运算符（如 `+`，`-`，`*`，`/`）的表达式过长时，应选择下面的方式缩进：

**yes**

```python
income = (gross_wages
          + taxable_interest
          + (dividends - qualified_dividends)
          - ira_deduction
          - student_loan_interest)

income = gross_wages \
       + taxable_interest \
       + (dividends - qualified_dividends) \
       - ira_deduction \
       - student_loan_interest
```

**no**

```python
income = (gross_wages +
          taxable_interest +
          (dividends - qualified_dividends) -
          ira_deduction -
          student_loan_interest)

income = gross_wages + \
         taxable_interest + \
         (dividends - qualified_dividends) - \
         ira_deduction - \
         student_loan_interest
```



### 每行最大长度

本项目不对每行代码的最大长度进行限制，但建议对于 79 个字符以上的行进行换行，换行时以代码易读性为准，无需为了换行而牺牲代码易读性。



### 空行

- 文件开头的 `imports` 部分和其余部分之间应该空 2 行
- 类当中定义的方法之间空行不能超过 1 行
- 一个函数中用 1 行的空行分隔不同的逻辑块



### 源代码编码

源代码应使用 `utf-8` 编码。



### Imports

Imports 部分应始终位于源代码顶部，在文档或注释之后，在全局变量、局部变量定义之前。

Imports 部分分为 3 组，分别是

1. Python 标准库
2. 与代码相关的第三方库
3. 本地的模块和库

组间使用 1 行空行隔开，组内按照字母排序。

*建议使用 `isort` 库进行自动整理*



## 表达式中的空格

以下情况下，需要避免多余的空格

- ```
  Yes: spam(ham[1], {eggs: 2})
  Ne:  spam( ham[ 1 ], { eggs: 2 } )
  ```

- ```
  Yes: if x == 4: print x, y; x, y = y, x
  No:  if x == 4 : print x , y ; x , y = y , x
  ```

- 切片操作需要看作二元运算符来处理，不过有例外情况：切片如果被省略的话空格也可以省略

  **yes**

  ```python
  ham[1:9], ham[1:9:3], ham[:9:3], ham[1::3], ham[1:9:]
  ham[lower:upper], ham[lower:upper:], ham[lower::step]
  ham[lower+offset : upper+offset]
  ham[: upper_fn(x) : step_fn(x)], ham[:: step_fn(x)]
  ham[lower + offset : upper + offset]
  ```

  **no**

  ```python
  ham[lower + offset:upper + offset]
  ham[1: 9], ham[1 :9], ham[1:9 :3]
  ham[lower : : upper]
  ham[ : upper]
  ```

- 使用 `()` 或  `[]` 操作时不需要和变量名之间空格

  ```python
  # Yes
  spam(1)
  dct['key'] = lst[index]
  # No
  spam (1)
  dct ['key'] = lst [index]
  ```



### 其它建议

- 函数的默认参数复制时不需要空格

  **yes**

  ```python
  def complex(real, imag=0.0):
      return magic(r=real, i=imag)
  ```

  **no**

  ```python
  def complex(real, imag = 0.0):
      return magic(r = real, i = imag)
  ```

- 类型声明需要空格

  **yes**

  ```python
  def munge(input: AnyStr): ...
  def munge() -> AnyStr: ...
  ```

  **no**

  ```python
  def munge(input:AnyStr): ...
  def munge()->PosInt: ...
  ```

- 既有类型声明，又有默认值时，需要空格

  **yes**

  ```python
  def munge(sep: AnyStr = None): ...
  def munge(input: AnyStr, sep: AnyStr = None, limit=1000): ...
  ```

  **no**

  ```python
  def munge(input: AnyStr=None): ...
  def munge(input: AnyStr, limit = 1000): ...
  ```



## 注释

当代码发生变化时，请先更新注释！

注释应该是完整的句子。如果注释是一个短语或句子，其第一个单词应该大写，除非它是一个以小写字母开头的标识符（永远不要改变标识符的大小写！）。

如果注释很短，可以省略句尾的句号。块注释通常由一个或多个由完整句子构成的段落组成，每个句子都应以句号结尾。

请用英语编写注释，除非你百分之百确定这块代码永远不会被不懂中文的人阅读。



### 文档注释

参考 [PEP 257](https://legacy.python.org/dev/peps/pep-0257/)