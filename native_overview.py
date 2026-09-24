"""Canvas-based native dashboard, sharing the web edition's visual language."""
import tkinter as tk

THEMES = {
    'light': dict(bg='#f3f6fc', surface='#ffffff', inset='#f7f9fd', border='#e1e8f3', text='#18263d', muted='#77869c', accent='#4268ea', soft='#eaf0ff', green='#159b7e'),
    'dark': dict(bg='#101722', surface='#192432', inset='#1e2c3d', border='#2b3b50', text='#edf3fc', muted='#92a5be', accent='#83a8ff', soft='#253d64', green='#58c9ac'),
}
PALETTE=['#4876f0','#25b798','#a27aef','#e6aa42','#e77d9c','#46b6cc']


def compact(n):
    if n >= 100000000: return f'{n/100000000:.2f}亿'
    if n >= 10000: return f'{n/10000:.1f}万'
    return f'{n:,}'


class Overview(tk.Frame):
    def __init__(self,parent):
        super().__init__(parent)
        self.theme='light'; self.data=None; self.tips={}; self.tip=None
        self.canvas=tk.Canvas(self,highlightthickness=0)
        scroll=tk.Scrollbar(self,orient='vertical',command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right',fill='y'); self.canvas.pack(fill='both',expand=True)
        self.canvas.bind('<Configure>',lambda e:self.draw())
        self.canvas.bind('<MouseWheel>',self.wheel)
        self.canvas.bind('<Motion>',self.hover)
        self.canvas.bind('<Leave>',lambda e:self.hide_tip())

    def wheel(self,event):
        self.hide_tip();self.canvas.yview_scroll(-int(event.delta/120)*3,'units')

    def hide_tip(self):
        if self.tip: self.tip.destroy();self.tip=None

    def hover(self,event):
        self.hide_tip()
        x,y=self.canvas.canvasx(event.x),self.canvas.canvasy(event.y)
        tip=next((self.tips[i] for i in reversed(self.canvas.find_overlapping(x-3,y-3,x+3,y+3)) if i in self.tips),None)
        if tip:
            self.tip=tk.Toplevel(self);self.tip.overrideredirect(True)
            tk.Label(self.tip,text=tip,bg='#263650',fg='white',justify='left',font=('Microsoft YaHei UI',10),padx=14,pady=10).pack()
            self.tip.update_idletasks()
            x=min(event.x_root+14,self.winfo_screenwidth()-self.tip.winfo_reqwidth()-8)
            y=min(event.y_root+16,self.winfo_screenheight()-self.tip.winfo_reqheight()-8)
            self.tip.geometry(f'+{max(0,x)}+{max(0,y)}')

    def box(self,x,y,w,h,fill=None,r=14):
        c=self.canvas;p=self.p
        return c.create_polygon(x+r,y,x+w-r,y,x+w,y,x+w,y+r,x+w,y+h-r,x+w,y+h,x+w-r,y+h,x+r,y+h,x,y+h,x,y+h-r,x,y+r,x,y, smooth=True,fill=fill or p['surface'],outline=p['border'])

    def text(self,x,y,text,size=10,color=None,bold=False,**kwargs):
        # Canvas geometry is in pixels; negative font sizes avoid a second
        # DPI scaling pass on Windows high-density displays.
        return self.canvas.create_text(x,y,text=text,anchor='nw',fill=color or self.p['text'],font=('Microsoft YaHei UI',-round(size*1.3),'bold' if bold else 'normal'),**kwargs)

    def title(self,x,y,eyebrow,title,description):
        self.text(x,y,eyebrow,8,self.p['accent'],True)
        self.text(x,y+23,title,14,bold=True)
        self.text(x,y+53,description,9,self.p['muted'])

    def set(self,data,theme=None):
        self.data=data
        if theme:self.theme=theme
        self.draw()

    def draw(self):
        c=self.canvas;self.p=p=THEMES[self.theme]
        c.configure(bg=p['bg']);self.configure(bg=p['bg'])
        self.hide_tip();c.delete('all');self.tips={}
        if not self.data:return
        d=self.data;w=max(680,c.winfo_width());margin=14;gap=18;inner=w-margin*2
        # Model cards retain provider attribution, like the browser edition.
        totals={}
        for row in d['daily_model_usage']:
            key=(row['model'],row['provider_label'])
            t=totals.setdefault(key,[0,0,0,0])
            for i,field in enumerate(['total_tokens','request_count','input_tokens','output_tokens']):t[i]+=row[field]
        models=sorted(totals.items(),key=lambda item:-item[1][0])
        cols=4 if inner>1150 else 3 if inner>850 else 2
        cardw=(inner-48-(cols-1)*12)/cols
        count=min(len(models),8)
        height=112+max(1,(count+cols-1)//cols)*156
        self.box(margin,14,inner,height)
        self.title(margin+24,34,'MODEL INSIGHTS','模型 Token 统计','按用量排序 · 同名模型按供应商独立统计 · 完整明细见「模型统计」')
        total=d['summary']['total_tokens']
        for i,((model,provider),values) in enumerate(models[:8]):
            x=margin+24+(i%cols)*(cardw+12);y=112+(i//cols)*156
            self.box(x,y,cardw,140,p['inset'],10)
            self.text(x+14,y+12,model if len(model)<27 else model[:24]+'…',11,bold=True)
            self.text(x+14,y+36,provider,9,p['muted'])
            item=self.text(x+14,y+57,compact(values[0]),23,bold=True)
            self.tips[item]=f'{model} · {provider}\nTotal：{values[0]:,}\nInput：{values[2]:,}\nOutput：{values[3]:,}'
            self.box(x+14,y+102,cardw-28,5,p['soft'],2)
            ratio=values[0]/max(1,total)
            c.create_rectangle(x+14,y+102,x+14+max(2,(cardw-28)*ratio),y+107,fill=PALETTE[i%len(PALETTE)],outline='')
            self.text(x+14,y+115,f'{ratio:.1%} 占比  ·  {values[1]:,} 次请求',9,p['muted'])
        if not models:self.text(margin+24,130,'当前筛选组合暂无数据',12,p['muted'])
        y=height+gap+14
        pair=inner>1000; panelw=(inner-gap)/2 if pair else inner
        self.workspace(margin,y,panelw,470,d)
        self.activity(margin+panelw+gap if pair else margin,y if pair else y+488,panelw,470,d)
        y+=488 if pair else 976
        self.box(margin,y,inner,335)
        self.title(margin+24,y+20,'REQUEST GRAIN','单次请求 Token 大小分布','鼠标指向柱形查看请求数 · 分位数表示指定比例请求不超过的 Token 数')
        dist=d['request_token_distribution']
        for i,key in enumerate(['p50','p90','p99']):
            self.text(margin+24+i*inner/3,y+93,f'{key.upper()}   {compact(dist[key])} Token',12,p['accent'],True)
        rows=dist['histogram'];maximum=max(1,max(r['count'] for r in rows));slot=(inner-64)/len(rows)
        for i,r in enumerate(rows):
            x=margin+32+i*slot;barh=r['count']/maximum*140
            item=c.create_rectangle(x,y+282-barh,x+slot-12,y+282,fill=p['accent'],outline='')
            self.tips[item]=f"{r['bucket']} Token\n请求数：{r['count']:,}"
            self.text(x,y+290,r['bucket'],9,p['muted'])
        c.configure(scrollregion=(0,0,w,y+355))

    def workspace(self,x,y,w,h,d):
        self.box(x,y,w,h);self.title(x+24,y+20,'WHERE WORK HAPPENS','工作空间活跃分布','按请求数排序 · 鼠标指向查看完整路径与用量')
        rows=sorted(d['workspace_distribution'],key=lambda r:-r['request_count'])[:10]
        maximum=max([1]+[r['request_count'] for r in rows])
        for i,r in enumerate(rows):
            yy=y+108+i*32
            name=r['workspace'].replace('\\','/').rstrip('/').split('/')[-1]
            text=self.text(x+24,yy,name[:19]+('…' if len(name)>19 else ''),9,self.p['muted'])
            start=x+w*.43;length=w*.42
            self.box(start,yy+3,length,12,self.p['soft'],5)
            item=self.box(start,yy+3,max(3,length*r['request_count']/maximum),12,self.p['accent'],3)
            tip=f"{r['workspace']}\n请求数：{r['request_count']:,}\nToken：{r['total_tokens']:,}"
            self.tips[item]=self.tips[text]=tip
            self.text(x+w-60,yy,compact(r['request_count']),9)

    def activity(self,x,y,w,h,d):
        self.box(x,y,w,h);self.title(x+24,y+20,'WHEN IT HAPPENS','日活分布','每日请求趋势与 24 小时活跃分布 · 指向数据查看详情')
        c=self.canvas;p=self.p;rows=d['daily_activity'];maxv=max([1]+[r['request_count'] for r in rows])
        left=x+45;right=x+w-28;top=y+115;bottom=y+250;points=[]
        for ratio in [0,.5,1]:
            yy=bottom-(bottom-top)*ratio
            c.create_line(left,yy,right,yy,fill=p['border'])
        for i,r in enumerate(rows):
            xx=left+(right-left)*i/max(1,len(rows)-1);yy=bottom-r['request_count']/maxv*(bottom-top)
            points.extend([xx,yy])
            item=c.create_oval(xx-5,yy-5,xx+5,yy+5,fill=p['surface'],outline=p['accent'],width=2)
            self.tips[item]=f"{r['date']}\n请求数：{r['request_count']:,}\nToken：{r['total_tokens']:,}"
            if i%max(1,len(rows)//6)==0:self.text(xx-16,bottom+10,r['date'][5:],8,p['muted'])
        if len(points)>2:c.create_line(*points,fill=p['accent'],width=2)
        self.text(x+24,y+297,'24 小时分布',11,bold=True)
        hours=[[0,0] for _ in range(24)]
        for r in d['hourly_activity']:hours[r['hour']][0]+=r['request_count'];hours[r['hour']][1]+=r['total_tokens']
        maximum=max([1]+[v[0] for v in hours]);cell=(w-48)/12
        for i,(requests,tokens) in enumerate(hours):
            xx=x+24+i%12*cell;yy=y+335+i//12*49
            item=self.box(xx,yy,cell-4,26,p['accent'] if requests/maximum>.5 else p['soft'] if requests else p['inset'],5)
            self.tips[item]=f'{i:02}:00–{i+1:02}:00\n请求数：{requests:,}\nToken：{tokens:,}'
            self.text(xx+4,yy+28,str(i)+'时',8,p['muted'])
