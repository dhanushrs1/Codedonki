const externalQuestions = [
  // HTML (1-10)
  {
    language: "HTML",
    question: "Which tag is used for the main heading of a page?",
    code: '<!-- Example HTML structure -->\n<html>\n  <head>\n    <title>My Page</title>\n  </head>\n  <body>\n    <!-- Main heading goes here -->\n  </body>\n</html>',
    options: ["<h1>", "<p>", "<div>"],
    correctIndex: 0
  },
  {
    language: "HTML",
    question: "Which tag is used to create a paragraph?",
    code: '<!-- HTML paragraph example -->\n<html>\n  <body>\n    <!-- Paragraph content goes here -->\n  </body>\n</html>',
    options: ["<paragraph>", "<p>", "<text>"],
    correctIndex: 1
  },
  {
    language: "HTML",
    question: "What attribute specifies the source (URL) of an image?",
    code: '<img src="donkey.png">',
    options: ["href", "src", "link"],
    correctIndex: 1
  },
  {
    language: "HTML",
    question: "Which tag is used to create a hyperlink (link)?",
    code: '<!-- HTML link example -->\n<a href="https://example.com">\n  Click here to visit\n</a>',
    options: ["<link>", "<a>", "<href>"],
    correctIndex: 1
  },
  {
    language: "HTML",
    question: "What attribute tells a link where to go?",
    code: '<a href="https://codedonki.com">Visit</a>',
    options: ["src", "target", "href"],
    correctIndex: 2
  },
  {
    language: "HTML",
    question: "Which tag makes text bold?",
    code: '<!-- HTML text formatting -->\n<p>\n  This text is <strong>bold</strong>\n  and this is <b>also bold</b>\n</p>',
    options: ["<bold>", "<b>", "<important>"],
    correctIndex: 1
  },
  {
    language: "HTML",
    question: "Which tag makes text italic (slanted)?",
    code: '<!-- HTML text formatting -->\n<p>\n  This text is <em>italic</em>\n  and this is <i>also italic</i>\n</p>',
    options: ["<em>", "<italic>", "<i>"],
    correctIndex: 2
  },
  {
    language: "HTML",
    question: "What does HTML stand for?",
    code: '<!-- HTML stands for HyperText Markup Language -->\n<!DOCTYPE html>\n<html>\n  <head>\n    <title>HTML Example</title>\n  </head>\n  <body>\n    <h1>Welcome to HTML!</h1>\n  </body>\n</html>',
    options: ["HyperText Markup Language", "High Tech Modern Language", "Home Tool Markup Language"],
    correctIndex: 0
  },
  {
    language: "HTML",
    question: "Which tag contains all the visible content of a web page?",
    code: '',
    options: ["<head>", "<main>", "<body>"],
    correctIndex: 2
  },
  {
    language: "HTML",
    question: "Which tag creates a list with bullet points?",
    code: '',
    options: ["<ol>", "<ul>", "<list>"],
    correctIndex: 1
  },
  // CSS (11-20)
  {
    language: "CSS",
    question: "Which property changes the text color?",
    code: 'p { color: blue; }',
    options: ["text-color", "font-color", "color"],
    correctIndex: 2
  },
  {
    language: "CSS",
    question: "Which property changes the background color?",
    code: 'body { background-color: lightblue; }',
    options: ["bgcolor", "background-color", "background"],
    correctIndex: 1
  },
  {
    language: "CSS",
    question: "How do you select an element with class='button'?",
    code: '',
    options: ["#button", ".button", "button"],
    correctIndex: 1
  },
  {
    language: "CSS",
    question: "How do you select all paragraph (<p>) elements?",
    code: '',
    options: ["p", ".p", "<p>"],
    correctIndex: 0
  },
  {
    language: "CSS",
    question: "What does CSS stand for?",
    code: '',
    options: ["Cascading Style Sheets", "Creative Style System", "Computer Style Sheets"],
    correctIndex: 0
  },
  {
    language: "CSS",
    question: "Which property changes the size of the text?",
    code: 'h1 { font-size: 24px; }',
    options: ["text-size", "font-size", "size"],
    correctIndex: 1
  },
  {
    language: "CSS",
    question: "Which property adds space *outside* an element's border?",
    code: '',
    options: ["padding", "margin", "border-spacing"],
    correctIndex: 1
  },
  {
    language: "CSS",
    question: "Which property adds space *inside* an element's border?",
    code: '',
    options: ["margin", "spacing", "padding"],
    correctIndex: 2
  },
  {
    language: "CSS",
    question: "How do you link a CSS file named 'style.css' to an HTML file?",
    code: '',
    options: ['<style src="style.css">', '<link rel="stylesheet" href="style.css">', '<css href="style.css">'],
    correctIndex: 1
  },
  {
    language: "CSS",
    question: "Which property makes text bold?",
    code: 'p { font-weight: bold; }',
    options: ["font-style: bold;", "text-decoration: bold;", "font-weight: bold;"],
    correctIndex: 2
  },
  // JavaScript (21-30)
  {
    language: "JavaScript",
    question: "Which keyword is commonly used to declare a variable that can change?",
    code: '',
    options: ["const", "let", "var"],
    correctIndex: 1
  },
  {
    language: "JavaScript",
    question: "What will this code output?",
    code: 'console.log(10 + 5);',
    options: ["105", "15", "Error"],
    correctIndex: 1
  },
  {
    language: "JavaScript",
    question: "What will this code output?",
    code: 'console.log("Code" + "Donki");',
    options: ["Code Donki", "CodeDonki", "Error"],
    correctIndex: 1
  },
  {
    language: "JavaScript",
    question: "How do you find the number of items in an array?",
    code: 'let fruits = ["apple", "banana"];\nconsole.log(fruits.???);',
    options: ["count", "size", "length"],
    correctIndex: 2
  },
  {
    language: "JavaScript",
    question: "What does the '=' symbol do in `let score = 0;`?",
    code: '',
    options: ["Checks if score is 0", "Adds 0 to score", "Assigns 0 to score"],
    correctIndex: 2
  },
  {
    language: "JavaScript",
    question: "What is the symbol for multiplication?",
    code: '',
    options: ["x", "*", "#"],
    correctIndex: 1
  },
  {
    language: "JavaScript",
    question: "What is the symbol for division?",
    code: '',
    options: ["/", "\\", "%"],
    correctIndex: 0
  },
  {
    language: "JavaScript",
    question: "How do you write a single-line comment?",
    code: '',
    options: ["// comment", "/* comment */", "# comment"],
    correctIndex: 0
  },
  {
    language: "JavaScript",
    question: "Which value represents 'yes' or 'on'?",
    code: '',
    options: ["true", "false", "yes"],
    correctIndex: 0
  },
   {
    language: "JavaScript",
    question: "What will this output?",
    code: 'let name = "donki";\nconsole.log(name.toUpperCase());',
    options: ["donki", "Donki", "DONKI"],
    correctIndex: 2
  },
  // Python (31-40)
  {
    language: "Python",
    question: "Which function is used to display output on the screen?",
    code: '',
    options: ["display()", "output()", "print()"],
    correctIndex: 2
  },
  {
    language: "Python",
    question: "What will this code output?",
    code: 'print(20 + 3)',
    options: ["203", "23", "Error"],
    correctIndex: 1
  },
  {
    language: "Python",
    question: "What will this code output?",
    code: 'print("Java" + "Script")',
    options: ["JavaScript", "Java Script", "Error"],
    correctIndex: 0
  },
  {
    language: "Python",
    question: "How do you write a single-line comment?",
    code: '',
    options: ["// comment", "# comment", "/* comment */"],
    correctIndex: 1
  },
  {
    language: "Python",
    question: "What will this code output?",
    code: 'len("Hello")',
    options: ["4", "5", "6"],
    correctIndex: 1
  },
  {
    language: "Python",
    question: "What does `score = 100` mean?",
    code: '',
    options: ["Checks if score equals 100", "Assigns 100 to score", "Adds 100 to score"],
    correctIndex: 1
  },
  {
    language: "Python",
    question: "What is the symbol for multiplication?",
    code: '',
    options: ["x", "#", "*"],
    correctIndex: 2
  },
  {
    language: "Python",
    question: "What is the symbol for division?",
    code: '',
    options: ["%", "\\", "/"],
    correctIndex: 2
  },
  {
    language: "Python",
    question: "What will this output?",
    code: 'print("FUN".lower())',
    options: ["FUN", "fun", "Error"],
    correctIndex: 1
  },
  {
    language: "Python",
    question: "What will this code output?",
    code: 'print("Go! " * 3)',
    options: ["Go! Go! Go! ", "Go! 3", "Error"],
    correctIndex: 0
  },
  // C (41-50) Very Basic
  {
    language: "C",
    question: "Which function is the starting point for every C program?",
    code: '',
    options: ["start()", "main()", "begin()"],
    correctIndex: 1
  },
  {
    language: "C",
    question: "Which function is often used to print text to the console?",
    code: '',
    options: ["print()", "output()", "printf()"],
    correctIndex: 2
  },
  {
    language: "C",
    question: "How do you declare a variable for whole numbers?",
    code: '',
    options: ["number x;", "integer x;", "int x;"],
    correctIndex: 2
  },
  {
    language: "C",
    question: "What is the symbol for adding two numbers?",
    code: 'int sum = 5 + 3;',
    options: ["add", "&", "+"],
    correctIndex: 2
  },
  {
    language: "C",
    question: "What character usually ends a C statement?",
    code: '',
    options: [". (period)", "; (semicolon)", ": (colon)"],
    correctIndex: 1
  },
  {
    language: "C",
    question: "Which header file is needed for input/output functions like printf?",
    code: '#include <stdio.h>',
    options: ["input.h", "stdio.h", "output.h"],
    correctIndex: 1
  },
  {
    language: "C",
    question: "What does `int score = 0;` do?",
    code: '',
    options: ["Makes score zero forever", "Declares an integer `score` and sets it to 0", "Checks if score is 0"],
    correctIndex: 1
  },
  {
    language: "C",
    question: "What is the symbol for subtraction?",
    code: '',
    options: ["-", "_", "minus"],
    correctIndex: 0
  },
  {
    language: "C",
    question: "Which keyword is used for single characters?",
    code: 'char initial = \'D\';',
    options: ["character", "char", "letter"],
    correctIndex: 1
  },
  {
    language: "C",
    question: "What symbols usually surround the code inside a function like `main`?",
    code: '',
    options: ["( )", "[ ]", "{ }"],
    correctIndex: 2
  },
   // Java (51-60) Very Basic
  {
    language: "Java",
    question: "What is the name of the main function where a Java program starts?",
    code: '',
    options: ["start()", "run()", "main()"],
    correctIndex: 2
  },
  {
    language: "Java",
    question: "How do you print a line of text to the console?",
    code: '',
    options: ["printLine()", "Console.write()", "System.out.println()"],
    correctIndex: 2
  },
  {
    language: "Java",
    question: "How do you declare a variable for whole numbers?",
    code: '',
    options: ["number count;", "int count;", "integer count;"],
    correctIndex: 1
  },
  {
    language: "Java",
    question: "What is the symbol for adding two numbers?",
    code: 'int total = 10 + 5;',
    options: ["plus", "+", "&"],
    correctIndex: 1
  },
  {
    language: "Java",
    question: "What character usually ends a Java statement?",
    code: '',
    options: [". (period)", ", (comma)", "; (semicolon)"],
    correctIndex: 2
  },
  {
    language: "Java",
    question: "Which keyword is used for whole numbers?",
    code: '',
    options: ["integer", "whole", "int"],
    correctIndex: 2
  },
  {
    language: "Java",
    question: "What does `String message = \"Hello\";` do?",
    code: '',
    options: ["Creates a message variable holding text", "Checks if message is Hello", "Prints Hello"],
    correctIndex: 0
  },
  {
    language: "Java",
    question: "What is the symbol for subtraction?",
    code: '',
    options: ["sub", "_", "-"],
    correctIndex: 2
  },
  {
    language: "Java",
    question: "Which keyword is used for text?",
    code: '',
    options: ["Text", "String", "str"],
    correctIndex: 1
  },
  {
    language: "Java",
    question: "What symbols usually surround the code inside a method (function)?",
    code: '',
    options: ["< >", "{ }", "( )"],
    correctIndex: 1
  },
  // Additional Questions (61-75)
  {
    language: "HTML",
    question: "Which tag creates a numbered list?",
    code: '',
    options: ["<ul>", "<ol>", "<li>"],
    correctIndex: 1
  },
  {
    language: "CSS",
    question: "Which property centers text horizontally?",
    code: 'h1 { text-align: center; }',
    options: ["center", "text-align: center", "align: center"],
    correctIndex: 1
  },
  {
    language: "JavaScript",
    question: "What will this code output?",
    code: 'console.log(10 > 5);',
    options: ["true", "false", "Error"],
    correctIndex: 0
  },
  {
    language: "Python",
    question: "What will this code output?",
    code: 'print(10 > 5)',
    options: ["True", "False", "Error"],
    correctIndex: 0
  },
  {
    language: "C",
    question: "What will this code output?",
    code: 'printf("%d", 5 + 3);',
    options: ["8", "53", "Error"],
    correctIndex: 0
  },
  {
    language: "Java",
    question: "What will this code output?",
    code: 'System.out.println(7 + 2);',
    options: ["72", "9", "Error"],
    correctIndex: 1
  },
  {
    language: "HTML",
    question: "Which tag is used for the smallest heading?",
    code: '',
    options: ["<h1>", "<h6>", "<small>"],
    correctIndex: 1
  },
  {
    language: "CSS",
    question: "Which property changes the font family?",
    code: 'p { font-family: Arial; }',
    options: ["font", "font-family", "family"],
    correctIndex: 1
  },
  {
    language: "JavaScript",
    question: "What will this code output?",
    code: 'console.log("Hello".length);',
    options: ["4", "5", "6"],
    correctIndex: 1
  },
  {
    language: "Python",
    question: "What will this code output?",
    code: 'print(len("Python"))',
    options: ["5", "6", "7"],
    correctIndex: 1
  },
  {
    language: "C",
    question: "What will this code output?",
    code: 'printf("%c", \'A\');',
    options: ["A", "65", "Error"],
    correctIndex: 0
  },
  {
    language: "Java",
    question: "What will this code output?",
    code: 'System.out.println("Java".length());',
    options: ["3", "4", "5"],
    correctIndex: 1
  },
  {
    language: "HTML",
    question: "Which attribute adds alternative text to an image?",
    code: '<img src="logo.png" alt="Logo">',
    options: ["title", "alt", "text"],
    correctIndex: 1
  },
  {
    language: "CSS",
    question: "Which property makes text underlined?",
    code: 'a { text-decoration: underline; }',
    options: ["underline", "text-decoration: underline", "decoration: underline"],
    correctIndex: 1
  }
];