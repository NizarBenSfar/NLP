import os
import pandas as pd
import numpy as np
from tqdm import tqdm
import re
tqdm.pandas()



class DataCleanser:

    def __init__(self):
        self.df = pd.read_csv("data/twcs/twcs.csv")

        #self.subsampling()
        self.create_support_columns()
        self.support_columns_extractions()
        self.nodes_list = None
        self.tweet_ids = self.df.tweet_id.values
        self.starter_tweet_ids = self.df[self.df.in_response_to_tweet_id.isna()].tweet_id.values
        self.tread_information()
        self.save_df()

    def save_df(self):
        self.df.to_csv("data/twcs/clean_twcs.csv")

    def tread_information(self):
        self.nodes_list = NodesList(self.starter_tweet_ids, self)

    def subsampling(self, to_take=10000):
        self.df = self.df.sort_values(by="tweet_id").reset_index(drop=True)
        self.df = self.df.iloc[:to_take].copy()

    def create_support_columns(self):
        self.df["tread"] = np.NaN
        self.df["order"] = np.NaN
        self.df["company"] = np.NAN
        self.df["start"] = np.NaN
        self.df["end"] = np.NaN
        self.df["company_creator"] = np.NaN

    def support_columns_extractions(self):
        self.df["company"] = self.df.progress_apply(extract_company, axis=1)
        self.df["start"] = self.df.in_response_to_tweet_id.isna()
        self.df["end"] = self.df.response_tweet_id.isna()
        self.df["company_creator"] = self.df.progress_apply(user_company_check, axis=1)


class Node:
    order = 0

    def __init__(self, tweet_id, dc):
        row = dc.df[dc.df.tweet_id == tweet_id].to_dict(orient="records")[0]
        dc.df.loc[dc.df.tweet_id == tweet_id, "order"] = Node.order
        dc.df.loc[dc.df.tweet_id == tweet_id, "tread"] = NodesList.tread
        Node.order = Node.order + 1
        self.value = row
        if type(row["response_tweet_id"]) == str:
            self.children = [int(x) for x in row["response_tweet_id"].split(",")]
            list_to_check = self.children.copy()
            for c in list_to_check:
                if c not in dc.tweet_ids:
                    self.children.remove(c)
        else:
            self.children = []
        self.children_nodes = list()
        self.__go_deeper(dc)

    def __go_deeper(self, dc):
        for child in self.children:
            if self.__check_children(child, dc):
                self.children_nodes.append(self.__go_deeper_by_child(child, dc))

    @staticmethod
    def __go_deeper_by_child(child, dc):
        children_node = Node(child, dc)
        return children_node

    @staticmethod
    def __check_children(children, dc):
        return children in dc.tweet_ids

    def explore(self):
        print(self.value)
        for children in self.children_nodes:
            children.explore()

    def __repr__(self):
        return "{\n" + f"{self.value},\n {self.children}" + "".join([repr(s) for s in self.children_nodes]) + "\n}"

    def __str__(self):
        return "{\n" + f"{self.value}" + "\n}"


class NodesList:

    tread = 0

    def __init__(self, list_id, dc):
        self.nodes_list = list()
        for t in tqdm(range(len(list_id))):
            x = list_id[t]
            self.nodes_list.append(Node(x, dc))
            NodesList.tread = NodesList.tread + 1
            Node.order = 0


def decomposition(f):

    res = []
    if len(f.children_nodes) == 0:
        return [f.value]
    else:
        for c in f.children_nodes:
            tmp = [f.value, decomposition(c)]
            res.append(tmp)
    return res


def extract_company(row):
    tags = [x.replace("@", "") for x in re.findall(r'@\w+', row.text)]
    res = np.unique([x for x in tags if not x.isnumeric()])
    if len(res) == 0:
        if row.author_id.isnumeric():
            return np.NaN
        else:
            return row.author_id
    else:
        res = res[0]
        if res == row.author_id:
            return res
        else:
            if (res != row.author_id) & (not row.author_id.isnumeric()):
                return row.author_id
            else:
                return res


def user_company_check(row):

    if row.author_id.isnumeric():
        return False  #user
    else:
        return True  #company