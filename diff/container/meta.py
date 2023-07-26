


class DynamicClassMeta(type):
    def __new__(cls, name, bases, attrs):
        # 获取前端传递的字段信息
        fields = attrs.pop('fields', {})

        # 动态添加属性和方法
        for field, value in fields.items():
            attrs[field] = value

        # 创建类
        return super().__new__(cls, name, bases, attrs)


class DynamicClassBase(metaclass=DynamicClassMeta):
    pass


# fields = {
#     'name': 'Alice',
#     'age': 25,
#     "gender": 'famle'
# }


fields = {'Field 1': '1222', 'Field 2': '222', 'Field 3': '333'}
# 动态生成类
DynamicClass = type('DynamicClass', (DynamicClassBase,), fields)

# 动态生成对象
obj = DynamicClass()

print(obj.keys)
# 访问对象的属性
# print(obj.name)  # 输出：Alice
# print(obj.age)  # 输出：25
# print(obj.gender)  # 输出：25

#
# if __name__ == '__main__':
#     import re
#
#     string = "root['CIC0001977']"
#     result = re.sub(r"root\['(.*)'\]", r"\1", string)
#
#     print(result)