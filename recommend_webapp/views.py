from django.shortcuts import render,redirect
from recommend_webapp.models import user
import pickle
import json
""" import pandas
import numpy """
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import requests
# Create your views here.
fn=''
ln=''
un=''
pwd=''
genrelist=[0,0,0,0,0,0,0]
new=pickle.load(open('new.pkl','rb'))
similarity=pickle.load(open('similarity.pkl','rb'))

def login(request):
    global un , pwd 
    if request.method=='POST':
        un=request.POST.get('username')
        pwd=request.POST.get('password')
        try:
            tempun=user.objects.get(username=un)
        except:
            return render(request,'login_page.html')
        if tempun.password==pwd:
            return redirect('http://localhost:8000/webapp/')
    return render(request,'login_page.html')


def signup(request):
    un=''
    fn=''
    ln=''
    pwd=''
    disc=''
    genrelist=[0,0,0,0,0,0,0]
    if request.method=='POST':
        d=request.POST
        for key,value in d.items():
            if key=="first_name":
                fn=value
            if key=="last_name":
                ln=value
            if key=="username":
                un=value
            if key=="password":
                pwd=value
            if key == "description": 
                str_list = value.split(",")
                movie_str=""
                for k in str_list:
                    k=remove_sp(k)
                    movie_str=movie_str + k +" "
                disc=disc+" "+movie_str
            if key=="genre":
                k=request.POST.getlist('genre')
                len_k=len(k)
                for i in range(len_k):
                    if k[i]=='action':
                        genrelist[0]=1
                    elif k[i]=='adventure':
                        genrelist[1]=1
                    elif k[i]=='romantic':
                        genrelist[2]=1
                    elif k[i]=='horror':
                        genrelist[3]=1
                    elif k[i]=='mystry':
                        genrelist[4]=1
                    elif k[i]=='scifi':
                        genrelist[5]=1
                    elif k[i]=='comedy':
                        genrelist[6]=1
            if key =="roduction house":
                k=request.POST.getlist('roduction house')
                listToStr = ' '.join(map(str, k))
                disc=disc+" "+listToStr
            if key =="Cast":
                k=request.POST.getlist('Cast')
                listToStr = ' '.join(map(str, k))
                disc=disc+" "+listToStr
            if key =="Director":
                k=request.POST.getlist('Director')
                listToStr = ' '.join(map(str, k))
                disc=disc+" "+listToStr
        User=user(First_name=fn,Last_name=ln,username=un,password=pwd,action=genrelist[0],adventure=genrelist[1],romantic=genrelist[2],horror=genrelist[3],mystery=genrelist[4],scifi=genrelist[5],comedy=genrelist[6],desc=disc)
        User.save()
    return render(request,'signup_page.html')


def webapp(request):
    global un
    tempun=user.objects.get(username=un)
    descr=tempun.desc
    tup=[0,0,0,0,0,0,0]
    if tempun.action==1:
        tup[0]=1
    if tempun.adventure==1:
        tup[1]=1
    if tempun.romantic==1:
        tup[2]=1
    if tempun.horror==1:
        tup[3]=1
    if tempun.mystery==1:
        tup[4]=1
    if tempun.scifi==1:
        tup[5]=1
    if tempun.comedy==1:
        tup[6]=1
    fmovie_list=get_recommended_by_prefrence(tup,descr)
    #like button working
    if request.method=='POST':
        likemove=request.POST.get('likebutton')
        print(likemove)
        jsonDec = json.decoder.JSONDecoder()
        try:
            likemovielist=jsonDec.decode(tempun.likedmovies)
        except:
            likemovielist=[]
        chk=0
        for i in likemovielist:
            if i==likemove:
                chk=1
                likemovielist.remove(i)
        if chk == 0:
            likemovielist.append(likemove)
        tempun.likedmovies=json.dumps(likemovielist)
        tempun.save()
    #recommendation on likes
    recommended_onlike=[]
    try:
        likemovielist=jsonDec.decode(tempun.likedmovies)
    except:
        likemovielist=[]
    print(likemovielist)
    for i in likemovielist:
        movie_id_for_re=int(i)
        recommended_onlike.extend(recommend(movie_id_for_re))


    #using api to fetch data
    movie_data=[]
    for i in fmovie_list:
        m_dict=get_data_api(i)
        movie_data.append(m_dict)
    
    movie_data2=[]
    for i in recommended_onlike:
        like_m_dict=get_data_api(i)
        movie_data2.append(like_m_dict)
    
    context={'movielist':movie_data,'username':un,'likemovie':movie_data2}
    return render(request,'webapp.html',context)



#functions for recommendations
def get_data_api(i):
    m_dict={}
    response=requests.get('https://api.themoviedb.org/3/movie/{}?api_key=fd1416b19d2f05c026f3e6327bda9d61&language=en-US'.format(i))
    data=response.json()
    m_dict['m_name']=data['original_title']
    try:
        m_dict['m_poster']= "https://image.tmdb.org/t/p/w500/"+data['poster_path']
    except:
        m_dict['m_poster']= "https://cdn.pixabay.com/photo/2019/11/07/20/48/cinema-4609877_960_720.jpg"
    m_dict['m_desc']=data['overview']
    m_dict['m_vote']=data['vote_average']
    m_dict['m_id']=data['id']
    return m_dict
def recommend(movie):
    m_list=[]
    index = new[new['movie_id'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])),reverse=True,key = lambda x: x[1])
    for i in distances[1:4]:
        m_list.append(new.iloc[i[0]].movie_id)
    return m_list

def get_recommended_by_prefrence(tup,str):  
    m_list=[]
    pref=''
    if tup[0]==1:
        pref+='action '
    if tup[1]==1:
        pref+='adventure '
    if tup[2]==1:
        pref+='romantic '
    if tup[3]==1:
        pref+='horror '
    if tup[4]==1:
        pref+='mystery '
    if tup[5]==1:
        pref+='ScienceFiction '
    if tup[6]==1:
        pref+='comedy '
    pref+=str
    pref_list=[pref]
    pref_list.extend(new['tags'])
    cv = CountVectorizer(max_features=5000,stop_words='english')
    pref_vector=cv.fit_transform(pref_list).toarray()
    similar_to_pref=cosine_similarity(pref_vector)
    distances = sorted(list(enumerate(similar_to_pref[0])),reverse=True,key = lambda x: x[1])
    for i in distances[1:17]:
        m_list.append(new.iloc[i[0]-1].movie_id)
    return m_list



def remove_sp(str):
    return str.replace(" ", "")