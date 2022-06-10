from rest_framework import serializers
from api import models


class CreateCommentSerializer(serializers.ModelSerializer):
    create_datetime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    # 'news', "reply", "content"
    # 根评论：news、content,reply=null,depth=0，root=null
    # 子评论：news、content,reply=回复的评论ID，depth=回复的评论深度+1，root=读回复的评论root=null或depth=0 ==读回复的评论;===读回复的评论.root
    # descendant_update_datetime根评论最近的更新时间；
    class Meta:
        model = models.Comment
        fields = ['news', "reply", "content", 'depth', "create_datetime"]
        read_only_fields = ['depth', ]
        extra_kwargs = {'news': {'write_only': True}}


class ListCommentSerializer(serializers.ModelSerializer):
    create_datetime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    children = serializers.SerializerMethodField()

    class Meta:
        model = models.Comment
        fields = ['create_datetime', "reply", "content", 'children']

    def get_children(self, obj):

        # 获取当前根评论的所有的子孙评论（后台）
        descendant_queryset = models.Comment.objects.filter(root=obj).order_by('id')

        descendant_dict = {}
        """
        {
            11:{"reply": 2, children:[
                13->{,"reply": 11, children:[
                    15:{"reply": 13, children:[
                        16:{"reply": 15, children:[],"content": "oooadfa;skdjf;akjsd;flkjasdf","depth": 4, "create_datetime": "2021-09-01 22:32:22"}
                    ],"content": "oooadfa;skdjf;akjsd;flkjasdf","depth": 3, "create_datetime": "2021-09-01 22:32:22"}
                ],"content": "oooadfa;skdjf;akjsd;flkjasdf","depth": 2, "create_datetime": "2021-09-01 22:32:22"}
            ],"content": "oooadfa;skdjf;akjsd;flkjasdf","depth": 1, "create_datetime": "2021-09-01 22:32:22"}
            12:{"reply": 2, children:[
                14->{"reply": 12, children:[],"content": "oooadfa;skdjf;akjsd;flkjasdf","depth": 2, "create_datetime": "2021-09-01 22:32:22"}
            ],"content": "oooadfa;skdjf;akjsd;flkjasdf","depth": 1, "create_datetime": "2021-09-01 22:32:22"}


            13:{"reply": 11, children:[
                15:{"reply": 13, children:[],"content": "oooadfa;skdjf;akjsd;flkjasdf","depth": 3, "create_datetime": "2021-09-01 22:32:22"}
            ],"content": "oooadfa;skdjf;akjsd;flkjasdf","depth": 2, "create_datetime": "2021-09-01 22:32:22"}
            14:{"reply": 12, children:[],"content": "oooadfa;skdjf;akjsd;flkjasdf","depth": 2, "create_datetime": "2021-09-01 22:32:22"}
            15:{"reply": 13, children:[
                16:{"reply": 15, children:[],"content": "oooadfa;skdjf;akjsd;flkjasdf","depth": 4, "create_datetime": "2021-09-01 22:32:22"}
            ],"content": "oooadfa;skdjf;akjsd;flkjasdf","depth": 3, "create_datetime": "2021-09-01 22:32:22"}
            16:{"reply": 15, children:[],"content": "oooadfa;skdjf;akjsd;flkjasdf","depth": 4, "create_datetime": "2021-09-01 22:32:22"}
        }
        """
        for descendant in descendant_queryset:
            ser = CreateCommentSerializer(instance=descendant, many=False)
            row = {'children': []}
            row.update(ser.data)
            descendant_dict[descendant.id] = row

        # 根评论obj的1级评论
        children_list = [
            # # 11
            # {"reply": 2, children:[],"content": "oooadfa;skdjf;akjsd;flkjasdf","depth": 1, "create_datetime": "2021-09-01 22:32:22"},
            # # 12
            # {"reply": 2, children:[],"content": "oooadfa;skdjf;akjsd;flkjasdf","depth": 1, "create_datetime": "2021-09-01 22:32:22"}
        ]
        for cid, item in descendant_dict.items():
            depth = item['depth']
            if depth == 1:
                children_list.append(item)
                continue
            reply_id = item['reply']
            descendant_dict[reply_id]['children'].append(item)

        return children_list
