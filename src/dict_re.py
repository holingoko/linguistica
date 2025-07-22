import re

tag_expression_regex = r"(\{[^{}]*?\{.*?\}[^{}]*?\}|\{[^{}]*?[^{}]*?\})(\|(\{[^{}]*?\{.*?\}[^{}]*?\}|\{[^{}]*?[^{}]*?\}))*"
tag_expression_pattern = re.compile(tag_expression_regex)
sub_expression_regex = r"\{[^{}]*?\}"
sub_expression_pattern = re.compile(sub_expression_regex)
reversed_tag = "{<-}"
escaped_left_curly_brace = r"\\{"
escaped_left_curly_brace_pattern = re.compile(escaped_left_curly_brace)
escaped_right_curly_brace = r"\\}"
escaped_right_curly_brace_pattern = re.compile(escaped_right_curly_brace)
bar_regex = r"\|"
bar_pattern = re.compile(bar_regex)
escaped_ellipsis_regex = r"\\..."
escaped_ellipsis_pattern = re.compile(escaped_ellipsis_regex)
left_curly_brace = "__LEFT_CURLY_BRACE__"
right_curly_brace = "__RIGHT_CURLY_BRACE__"
vertical_bar = "__VERTICAL_BAR__"
ellipsis_ = "__ELLIPSIS__"
valid_tag_regex = r"[\w ]+"
valid_tag_pattern = re.compile(valid_tag_regex)


def parse(in_):
    in_ = replace_non_conditional_vertical_bar(in_)
    out, conditionals = parse_format(in_)
    return out, [
        parse_conditional(conditional) for conditional in conditionals
    ]


def parse_format(in_):
    out_list = []
    conditionals = []
    prev_match_end = 0
    for match in tag_expression_pattern.finditer(in_):
        match_start = match.start()
        out_list.append(
            in_[prev_match_end:match_start],
        )
        prev_match_end = match.end()
        out_list.append("{}")
        conditionals.append(match.group())
    out_list.append(in_[prev_match_end:])
    out = "".join(out_list)
    return out, conditionals


def parse_conditional(in_):
    out = []
    in_ = replace_non_conditional_vertical_bar(in_)
    for expression in in_.split("|"):
        expression = expression.replace(vertical_bar, "|")
        out.append(parse_expression(expression))
    return out


def replace_non_conditional_vertical_bar(in_):
    bar_indices = [match.start() for match in bar_pattern.finditer(in_)]
    out_list = list(in_)
    for i in reversed(bar_indices):
        preceding_chars = in_[:i]
        if preceding_chars.count("{") != preceding_chars.count("}"):
            out_list[i] = vertical_bar
    out = "".join(out_list)
    return out


def parse_expression(in_):
    in_ = in_[1:-1]
    if "{" not in in_:
        return "{}", [in_]
    out_list = []
    tags = []
    prev_match_end = 0
    for match in sub_expression_pattern.finditer(in_):
        match_start = match.start()
        out_list.append(
            in_[prev_match_end:match_start],
        )
        prev_match_end = match.end()
        out_list.append("{}")
        tags.append(match.group()[1:-1])
    out_list.append(in_[prev_match_end:])
    out = "".join(out_list)
    return out, tags


def parse_option_tags(in_):
    order_reversed = reversed_tag in in_
    in_ = in_.replace(reversed_tag, "")
    return in_, (order_reversed,)


def expand_tag_values_format_expression(in_, num_values):
    in_ = replace_non_continuation_ellipsis(in_)
    ellipsis_index = in_.find("...")
    if ellipsis_index == -1:
        if in_.count("{}") == num_values:
            return in_.replace(ellipsis_, "...")
        else:
            return ""
    left = in_[:ellipsis_index]
    right = in_[ellipsis_index + 3 :]
    left_split = left.split("{}")
    right_split = right.split("{}")
    if len(left_split) == 1:
        left_split = left_split + [""]
    if len(right_split) == 1:
        right_split = [""] + right_split
    left_joins = left_split[1:-1]
    right_joins = right_split[1:-1]
    left_end = left_split[0]
    right_end = right_split[-1]
    default_join = left_split[-1] + right_split[0]
    num_braces = len(left_joins) + len(right_joins) + 1
    if num_braces > num_values:
        return ""
    num_braces_needed = num_values - num_braces
    out = (
        left_end
        + ("{}" + "{}".join(left_joins) if left_joins else "")
        + f"{{}}{default_join}" * num_braces_needed
        + ("{}" + "{}".join(right_joins) if right_joins else "")
        + "{}"
        + right_end
    )
    return out.replace(ellipsis_, "...")


def replace_non_continuation_ellipsis(in_):
    return escaped_ellipsis_pattern.sub(ellipsis_, in_)


def replace_non_tag_curly_braces(in_):
    out = escaped_left_curly_brace_pattern.sub(left_curly_brace, in_)
    out = escaped_right_curly_brace_pattern.sub(right_curly_brace, out)
    return out


def restore_non_tag_curly_braces(in_):
    return in_.replace(left_curly_brace, "{").replace(right_curly_brace, "}")


def check_tag_valid(tag):
    return bool(valid_tag_pattern.fullmatch(tag))
