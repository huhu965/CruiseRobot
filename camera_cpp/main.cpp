#include <iostream>
#include<iomanip>
#include <cstdio>
#include <cstdlib>
#include<cstring>
#include <algorithm>
#include <cmath>
#include <cctype>

using namespace std;

class Set
{
    struct Linklist              //定义链表
    {
        int date;
        Linklist *next;
    };

private:
    Linklist *head;
public:
    Set();                      //构造函数
    Set(const Set& rhs);        //复制构造
    ~Set();

    Set& operator = (const Set& rhs);
    Set  operator + (const Set& rhs);
    Set  operator - (const Set& rhs);
    Set  operator * (const Set& rhs);

    void insert(int val);
    void erase(int val);
    bool find(int val);
    bool empty();
    void show();
};

Set::Set()
{
    head = new Linklist;
    head->next = NULL;
}

Set::Set(const Set& rhs)
{
    head = new Linklist;
    head->next = NULL;

    Linklist* last = head;
    Linklist* tem = rhs.head->next;

    while(tem != NULL)
    {
        Linklist* p = new Linklist;
        p->date = tem->date;

        last->next = p;
        last = last->next;
        tem = tem->next;
    }
    last->next = NULL;
}

Set::~Set()
{
    while(head != NULL)
    {
        Linklist* tem = head;
        head = head->next;

        delete tem;
    }
}

Set& Set::operator=(const Set& rhs)
{
    this->~Set();
    this->head = NULL;

    this->head = new Linklist;
    this->head->next = NULL;

    Linklist* last = this->head;
    Linklist* tem = rhs.head->next;

    while(tem != NULL)
    {
        Linklist* p = new Linklist;
        p->date = tem->date;

        last->next = p;
        last = last->next;
        tem = tem->next;
    }
    last->next = NULL;

    return *this;
}

Set Set::operator+(const Set& rhs)
{
    Set res = *this;

    Linklist* tem = rhs.head->next;
    while(tem != NULL)
    {
        res.insert(tem->date);
        tem = tem->next;
    }

    return res;
}

Set Set::operator*(const Set& rhs)
{
    Set res;

    Linklist* tem = rhs.head->next;
    while(tem != NULL)
    {
        int val = tem->date;
        if(this->find(val))
        {
            res.insert(val);
        }

        tem = tem->next;
    }

    return res;
}

Set Set::operator-(const Set& rhs)
{
    Set res = *this;

    Linklist *tem = rhs.head->next;

    while(tem != NULL)
    {
        int val = tem->date;
        res.erase(val);

        tem = tem->next;
    }

    return res;
}

void Set::insert(int val)
{
    if(find(val)) return;

    Linklist *tem = head;
    while(tem->next != NULL && val > (tem->next->date))
    {
        tem = tem->next;
    }

    Linklist* p = new Linklist;
    p->date = val;
    p->next = tem->next;
    tem->next = p;
}

void Set::erase(int val)
{
    Linklist *tem = head;

    while(tem->next != NULL)
    {
        if(tem->next->date == val)
        {
            Linklist* p = tem->next;
            tem->next = tem->next->next;

            delete p;
            return;
        }
        tem = tem->next;
    }
}

bool Set::find(int val)
{
    Linklist *tem = head;

    while(tem->next != NULL)
    {
        if(tem->next->date == val) return true;
        tem = tem->next;
    }

    return false;
}

bool Set::empty()
{
    if(head == NULL)
    {
        head = new Linklist;
        head->next = NULL;
        return true;
    }
    return false;
}

void Set::show()
{
    cout << "{";

    Linklist *tem = head;
    while(tem->next != NULL)
    {
        if(tem != head)
            cout << ",";
        cout << tem->next->date;
        tem = tem->next;
    }
    cout << "}" << endl;
}

int main()
{
    int n,m;

    cin >> n >> m;

    Set a,b;

    for(int i=1 ; i<=n ; i++)
    {
        int x;
        cin >> x;
        a.insert(x);
    }

    for(int i=1 ; i<=m ; i++)
    {
        int x;
        cin >> x;
        b.insert(x);
    }

    a.show();
    b.show();

    Set c = a + b;
    c.show();

    Set d = a * b;
    d.show();

    Set e = a - b;
    e.show();

    return 0;
}
