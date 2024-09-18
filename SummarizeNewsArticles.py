import tkinter as tk
from textblob import TextBlob
from newspaper import Article
import nltk


def summarize():
    urls = url.get('1.0', 'end').strip()
    try:
        article = Article(urls)
        article.download()
        article.parse()
        article.nlp()

        title.config(state='normal')
        author.config(state='normal')
        publish.config(state='normal')
        summary.config(state='normal')
        sen.config(state='normal')

        title.delete('1.0', 'end')
        title.insert('1.0', article.title if article.title else "No Title Available")
        author.delete('1.0', 'end')
        author.insert('1.0', ', '.join(article.authors) if article.authors else "No Authors Available")
        publish.delete('1.0', 'end')
        publish.insert('1.0', str(article.publish_date) if article.publish_date else "No Date Available")
        summary.delete('1.0', 'end')
        summary.insert('1.0', article.summary if article.summary else "No Summary Available")

        if article.text:
            analysis = TextBlob(article.text)
            polarity = analysis.polarity
            sentiment_result = f'Polarity: {polarity:.2f}, Sentiment: '
            sentiment_result += "Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral"
        else:
            sentiment_result = "No text available for sentiment analysis."

        sen.delete('1.0', 'end')
        sen.insert('1.0', sentiment_result)

        title.config(state='disabled')
        author.config(state='disabled')
        publish.config(state='disabled')
        summary.config(state='disabled')
        sen.config(state='disabled')

    except Exception as e:
        clear_fields()
        sen.config(state='normal')
        sen.delete('1.0', 'end')
        sen.insert('1.0', f"Error: {str(e)}")
        sen.config(state='disabled')

def clear_fields():
    title.config(state='normal')
    author.config(state='normal')
    publish.config(state='normal')
    summary.config(state='normal')
    sen.config(state='normal')

    title.delete('1.0', 'end')
    author.delete('1.0', 'end')
    publish.delete('1.0', 'end')
    summary.delete('1.0', 'end')
    sen.delete('1.0', 'end')

    title.config(state='disabled')
    author.config(state='disabled')
    publish.config(state='disabled')
    summary.config(state='disabled')
    sen.config(state='disabled')

root = tk.Tk()
root.title('News Summarizer')
root.geometry('1080x800')

tlabel = tk.Label(root, text="Title")
tlabel.pack()

title = tk.Text(root, height=2, width=144, bg='#dddddd', wrap='word')
title.config(state='disabled')
title.pack()

alabel = tk.Label(root, text="Author")
alabel.pack()

author = tk.Text(root, height=2, width=144, bg='#dddddd', wrap='word')
author.config(state='disabled')
author.pack()

plabel = tk.Label(root, text="Publication Date")
plabel.pack()

publish = tk.Text(root, height=2, width=144, bg='#dddddd', wrap='word')
publish.config(state='disabled')
publish.pack()

slabel = tk.Label(root, text="Summary")
slabel.pack()

summary = tk.Text(root, height=20, width=144, bg='#dddddd', wrap='word')
summary.config(state='disabled')
summary.pack()

selabel = tk.Label(root, text="Sentiment Analysis")
selabel.pack()

sen = tk.Text(root, height=2, width=144, bg='#dddddd', wrap='word')
sen.config(state='disabled')
sen.pack()

ulabel = tk.Label(root, text="Enter URL")
ulabel.pack()

url = tk.Text(root, height=2, width=144, wrap='word')
url.pack()

btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

summarize_btn = tk.Button(btn_frame, text="Summarize", command=summarize)
summarize_btn.grid(row=0, column=0, padx=5)

clear_btn = tk.Button(btn_frame, text="Clear", command=clear_fields)
clear_btn.grid(row=0, column=1, padx=5)

root.mainloop()
