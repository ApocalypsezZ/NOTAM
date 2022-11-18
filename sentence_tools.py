import re
import pandas as pd

# 
def preprocess_sentence_code(sentence: str, action_words):
    '''
    '''
    # 去除 '.'
    sentence = sentence.replace('.', '')
    # 多个空格变一个空格
    sentence = ' '.join(sentence.split())
    # 大写化
    # 判断是否多动词共有主语
    match = re.search(r".*?(?={0}) .*(AND?={0})*".format(action_words), sentence, flags=re.I)
    if match:
        # 找出主语
        entity = re.search(r"(?P<entity>.*?)"+r"(?={0})".format(action_words), sentence, flags=re.I)
        entity = entity.group("entity")
        # 分割原句 
        sentence_split = re.sub(r" AND(?={0})".format(action_words), "|", sentence)
        sentence_ls = sentence_split.split('|')
        # 主语归位
        res_sentence_ls = []
        for i, s in enumerate(sentence_ls):
            if i == 0:
                res_sentence_ls.append(s)
            else:
                res_sentence_ls.append(entity + s)
        return res_sentence_ls
    else:
        return [sentence]

# sentence = "RWY 12 NOT AVBL DUE WIP EXC SNOW AND U/S DUE TO RAIN AND U/S" 
# action_words = " NOT AVBL| U/S"
# preprocess_sentence_code(sentence, action_words)


# 
def read_words(path, sheet_name='words_list'):
    '''
    '''
    df_words = pd.read_excel(path, sheet_name=sheet_name)
    verb_ls, limit_words_ls = set(df_words['ACTION'].values), set(df_words['LIMIT'].values)
    verb_ls, limit_words_ls = [word for word in verb_ls if isinstance(word, str)], [word for word in limit_words_ls if isinstance(word, str)]
    # entity = "ILS RWY|RWY"
    action = " " + "| ".join(verb_ls)
    reason = " DUE"
    # limit = " EXCEPT | EXC | EXP | WHEN | FOLLOWING CONDITIONS | ONLY | FLW LIMITATIONS | IN CASE OF "
    limit = " " + "| ".join(limit_words_ls)
    source = " REFER| REF"
    return action, reason, limit, source


# 
def get_item_pattern_list(action_words, reason_words, limit_words, source_words, path, sheet_name='base_rules', ):
    '''
    '''
    df_rules = pd.read_excel(path, sheet_name=sheet_name)
    format_ls = list(set(df_rules['FORMAT'].values))
    pattern_entity_ls, pattern_action_ls, pattern_reason_ls, pattern_limit_ls, pattern_source_ls = [], [], [], [], []
    for item in format_ls:
        if item == "entity":
            pattern_entity_ls = list(df_rules.loc[df_rules['FORMAT'] == item, 'RULES'].values)
        elif item == "action":
            pattern_action_ls = list(df_rules.loc[df_rules['FORMAT'] == item, 'RULES'].values)
        elif item == "reason":
            pattern_reason_ls = list(df_rules.loc[df_rules['FORMAT'] == item, 'RULES'].values)
        elif item == "limit":
            pattern_limit_ls = list(df_rules.loc[df_rules['FORMAT'] == item, 'RULES'].values)
        elif item == "source":
            pattern_source_ls = list(df_rules.loc[df_rules['FORMAT'] == item, 'RULES'].values)
        else:
            print("error")

    # pattern_entity_ls = [p.format(entity) for p in pattern_entity_ls]
    pattern_action_ls = [p.format(action_words) for p in pattern_action_ls]
    pattern_reason_ls = [p.format(reason_words) for p in pattern_reason_ls]
    pattern_limit_ls = [p.format(limit_words) for p in pattern_limit_ls]
    pattern_source_ls = [p.format(source_words) for p in pattern_source_ls]

    return pattern_entity_ls, pattern_action_ls, pattern_reason_ls, pattern_limit_ls, pattern_source_ls


# pattern combin
def pattern_combine(pattern_entity_ls, pattern_action_ls, pattern_reason_ls, pattern_limit_ls, pattern_source_ls):
    '''
    '''
    pattern_ls = []
    # 主语 + 动词 + 原因 + 限制 + 来源
    for p_entity in pattern_entity_ls:
        for pattern_action in pattern_action_ls:
            for p_reason in pattern_reason_ls:
                for p_limit in pattern_limit_ls:
                    for p_source in pattern_source_ls:
                        pattern_ls.append(p_entity + pattern_action + p_reason + p_limit + p_source)
    # 主语 + 动词 + 原因 + 限制
    for p_entity in pattern_entity_ls:
        for pattern_action in pattern_action_ls:
            for p_reason in pattern_reason_ls:
                for p_limit in pattern_limit_ls:
                    pattern_ls.append(p_entity + pattern_action + p_reason + p_limit)
    # 主语 + 动词 + 原因
    for p_entity in pattern_entity_ls:
        for pattern_action in pattern_action_ls:
            for p_reason in pattern_reason_ls:
                pattern_ls.append(p_entity + pattern_action + p_reason)
    # 主语 + 动词 + 限制
    for p_entity in pattern_entity_ls:
        for pattern_action in pattern_action_ls:
            for p_limit in pattern_limit_ls:
                pattern_ls.append(p_entity + pattern_action + p_limit)
    # 主语 + 动词 + 来源
    for p_entity in pattern_entity_ls:
        for pattern_action in pattern_action_ls:
            for p_source in pattern_source_ls:
                pattern_ls.append(p_entity + pattern_action + p_source)
    # 主语 + 动词
    for p_entity in pattern_entity_ls:
        for pattern_action in pattern_action_ls:
            pattern_ls.append(p_entity + pattern_action)
    # print(len(pattern_ls))
    return pattern_ls 


# general rules
def get_general_rules(path, words_sheet, rules_sheet):
    '''
    '''
    # read_words
    action_words, reason_words, limit_words, source_words = read_words(path=path, sheet_name=words_sheet)
    # get each item pattern list
    pattern_entity_ls, pattern_action_ls, pattern_reason_ls, pattern_limit_ls, pattern_source_ls = get_item_pattern_list(action_words, reason_words, limit_words, source_words, path=path, sheet_name=rules_sheet)
    # pattern combine 
    pattern_ls = pattern_combine(pattern_entity_ls, pattern_action_ls, pattern_reason_ls, pattern_limit_ls, pattern_source_ls)
    return pattern_ls


# pattern supply
def get_supplement_rules(path, words_sheet, rules_sheet):
    '''
    '''
    # read_words
    action_words, reason_words, limit_words, source_words = read_words(path=path, sheet_name=words_sheet)
    # read supplement_rules
    df_rules = pd.read_excel(path, sheet_name=rules_sheet)
    format_ls = list(set(df_rules['FORMAT'].values))
    print(format_ls)
    supplement_pattern_ls = []
    for item in format_ls:
        if item == "NONE":
            supplement_pattern_ls.extend(list(df_rules.loc[df_rules['FORMAT'] == item, 'RULES'].values))
        elif item == "action":
            supplement_pattern_ls.extend([rule.format(action_words) for rule in list(df_rules.loc[df_rules['FORMAT'] == item, 'RULES'].values)])
        elif item == "reason":
            supplement_pattern_ls.extend([rule.format(reason_words) for rule in list(df_rules.loc[df_rules['FORMAT'] == item, 'RULES'].values)])
        elif item == "limit":
            supplement_pattern_ls.extend([rule.format(limit_words) for rule in list(df_rules.loc[df_rules['FORMAT'] == item, 'RULES'].values)])
        elif item == "source":
            supplement_pattern_ls.extend([rule.format(source_words) for rule in list(df_rules.loc[df_rules['FORMAT'] == item, 'RULES'].values)])
        else:
            print("error")
    return supplement_pattern_ls

# RULES_TABLE = 'E:/Workstation/data/NOTAM/NOTAM_table.xlsx'
# SUPPLEMENT_RULES = get_supplement_rules(RULES_TABLE, words_sheet="words_list", rules_sheet="supplement_rules")
# len(SUPPLEMENT_RULES)