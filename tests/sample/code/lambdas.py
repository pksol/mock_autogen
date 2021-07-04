def simple_func_using_lambdas(items, other_items):
    unique_items = []
    for item in items:
        if not any(
                filter(
                    lambda other_item: len(item) and other_item.startswith(
                        item) or item.startwith(other_item), other_items)):
            unique_items.append(item)
    return unique_items
