#!/usr/bin/env python
"""
Database Query Tool - A simple terminal menu for querying the microblog database
"""
import os
import sys
import sqlite3
from datetime import datetime
from flask import Flask
from config import Config
from tabulate import tabulate

def clear_screen():
    """Clear the terminal screen based on OS"""
    os.system('cls' if os.name == 'nt' else 'clear')

def connect_to_db():
    """Connect to the SQLite database"""
    try:
        conn = sqlite3.connect('instance/app.db')
        conn.row_factory = sqlite3.Row  # This enables column access by name
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def execute_query(conn, query, params=(), fetch_all=True):
    """Execute SQL query and return results"""
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        
        if query.strip().lower().startswith(('select', 'pragma')):
            if fetch_all:
                return cur.fetchall()
            else:
                return cur.fetchone()
        else:
            conn.commit()
            return cur.rowcount  # Return number of affected rows
    except sqlite3.Error as e:
        print(f"Error executing query: {e}")
        return None

def display_results(results, title=None):
    """Display query results in a table format"""
    if not results:
        print("No results found.")
        return
    
    if title:
        print(f"\n{title}\n{'=' * len(title)}")
    
    if isinstance(results, list) and len(results) > 0:
        # Convert results to a list of dictionaries
        headers = results[0].keys()
        rows = [dict(row) for row in results]
        print(tabulate(rows, headers="keys", tablefmt="grid"))
        print(f"Total rows: {len(results)}")
    else:
        print(results)

def get_table_schema(conn, table_name):
    """Get the schema of a table"""
    query = f"PRAGMA table_info({table_name})"
    return execute_query(conn, query)

def list_tables(conn):
    """List all tables in the database"""
    query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    tables = execute_query(conn, query)
    
    clear_screen()
    print("\nAvailable Tables\n===============")
    for i, table in enumerate(tables, 1):
        print(f"{i}. {table['name']}")
    
    print("\nSelect a table to view schema (or 0 to return): ", end="")
    choice = input()
    
    try:
        choice = int(choice)
        if choice == 0:
            return
        
        if 1 <= choice <= len(tables):
            table_name = tables[choice-1]['name']
            schema = get_table_schema(conn, table_name)
            
            clear_screen()
            print(f"\nSchema for table: {table_name}\n")
            print(tabulate([dict(col) for col in schema], headers="keys", tablefmt="grid"))
            
            print("\nPress Enter to continue...", end="")
            input()
    except ValueError:
        print("Invalid choice. Press Enter to continue...", end="")
        input()

def show_all_users(conn):
    """Show all users in the database"""
    query = """
    SELECT id, username, email, last_seen
    FROM user
    ORDER BY username
    """
    users = execute_query(conn, query)
    
    clear_screen()
    display_results(users, "All Users")
    
    print("\nPress Enter to continue...", end="")
    input()

def show_all_posts(conn):
    """Show all posts with author information and like counts"""
    query = """
    SELECT p.id, p.body, p.timestamp, u.username as author,
           (SELECT COUNT(*) FROM like WHERE post_id = p.id) as likes
    FROM post p
    JOIN user u ON p.user_id = u.id
    ORDER BY p.timestamp DESC
    """
    posts = execute_query(conn, query)
    
    clear_screen()
    display_results(posts, "All Posts")
    
    print("\nPress Enter to continue...", end="")
    input()

def search_users(conn):
    """Search users by username or email"""
    clear_screen()
    print("\nSearch Users\n===========")
    search_term = input("Enter search term (username/email): ")
    
    query = """
    SELECT id, username, email, last_seen
    FROM user
    WHERE username LIKE ? OR email LIKE ?
    ORDER BY username
    """
    params = (f'%{search_term}%', f'%{search_term}%')
    users = execute_query(conn, query, params)
    
    display_results(users, f"Users matching '{search_term}'")
    
    print("\nPress Enter to continue...", end="")
    input()

def search_posts(conn):
    """Search posts by content"""
    clear_screen()
    print("\nSearch Posts\n===========")
    search_term = input("Enter search term: ")
    
    query = """
    SELECT p.id, p.body, p.timestamp, u.username as author,
           (SELECT COUNT(*) FROM like WHERE post_id = p.id) as likes
    FROM post p
    JOIN user u ON p.user_id = u.id
    WHERE p.body LIKE ?
    ORDER BY p.timestamp DESC
    """
    params = (f'%{search_term}%',)
    posts = execute_query(conn, query, params)
    
    display_results(posts, f"Posts containing '{search_term}'")
    
    print("\nPress Enter to continue...", end="")
    input()

def custom_query(conn):
    """Execute a custom SQL query"""
    clear_screen()
    print("\nCustom SQL Query\n==============")
    print("Enter your SQL query (or 'exit' to return to menu):")
    
    lines = []
    while True:
        line = input()
        if line.lower() == 'exit':
            return
        
        lines.append(line)
        if line.strip().endswith(';'):
            break
    
    query = " ".join(lines)
    if query.strip().endswith(';'):
        query = query.strip()[:-1]  # Remove trailing semicolon
    
    results = execute_query(conn, query)
    if results is not None:
        if isinstance(results, int):
            print(f"\n{results} rows affected")
        else:
            display_results(results, "Query Results")
    
    print("\nPress Enter to continue...", end="")
    input()

def add_post(conn):
    """Add a new post to the database"""
    clear_screen()
    print("\nAdd New Post\n===========")
    
    # Get list of users for selection
    users = execute_query(conn, "SELECT id, username FROM user ORDER BY username")
    
    print("Available users:")
    for i, user in enumerate(users, 1):
        print(f"{i}. {user['username']}")
    
    try:
        user_choice = int(input("\nSelect user (number): "))
        if not (1 <= user_choice <= len(users)):
            print("Invalid user selection.")
            return
        
        user_id = users[user_choice-1]['id']
        
        print("\nEnter post content (press Enter twice to finish):")
        lines = []
        while True:
            line = input()
            if not line and lines and not lines[-1]:
                break
            lines.append(line)
        
        post_body = "\n".join(lines).strip()
        
        if not post_body:
            print("Post content cannot be empty.")
            return
        
        query = """
        INSERT INTO post (body, user_id, timestamp)
        VALUES (?, ?, ?)
        """
        timestamp = datetime.utcnow().isoformat()
        params = (post_body, user_id, timestamp)
        
        result = execute_query(conn, query, params)
        if result:
            print(f"\nPost added successfully!")
    except ValueError:
        print("Invalid input.")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nPress Enter to continue...", end="")
    input()

def show_post_likes(conn):
    """Show all likes for a specific post"""
    clear_screen()
    print("\nShow Post Likes\n==============")
    
    # Get posts with like counts
    posts_query = """
    SELECT p.id, p.body, u.username as author, 
           (SELECT COUNT(*) FROM like WHERE post_id = p.id) as likes
    FROM post p
    JOIN user u ON p.user_id = u.id
    ORDER BY likes DESC, p.timestamp DESC
    """
    posts = execute_query(conn, posts_query)
    
    if not posts:
        print("No posts found.")
        print("\nPress Enter to continue...", end="")
        input()
        return
    
    # Display posts for selection
    print("\nAvailable posts:")
    print(tabulate([{
        'ID': post['id'],
        'Author': post['author'],
        'Post': post['body'][:50] + ('...' if len(post['body']) > 50 else ''),
        'Likes': post['likes']
    } for post in posts], headers="keys", tablefmt="grid"))
    
    try:
        post_id = int(input("\nEnter post ID to see likes (or 0 to return): "))
        if post_id == 0:
            return
        
        # Get likes for the selected post
        likes_query = """
        SELECT l.timestamp, u.username
        FROM like l
        JOIN user u ON l.user_id = u.id
        WHERE l.post_id = ?
        ORDER BY l.timestamp DESC
        """
        likes = execute_query(conn, likes_query, (post_id,))
        
        clear_screen()
        post = next((p for p in posts if p['id'] == post_id), None)
        
        if post:
            print(f"\nPost #{post_id} by {post['author']}:\n")
            print(f"{post['body']}")
            print(f"\nLikes: {post['likes']}")
            
            if likes:
                print("\nLiked by:")
                display_results(likes, "Users who liked this post")
            else:
                print("\nThis post has no likes yet.")
        else:
            print(f"Post #{post_id} not found.")
    except ValueError:
        print("Invalid post ID.")
    
    print("\nPress Enter to continue...", end="")
    input()

def show_user_likes(conn):
    """Show all posts liked by a specific user"""
    clear_screen()
    print("\nShow User Likes\n==============")
    
    # Get users
    users = execute_query(conn, "SELECT id, username FROM user ORDER BY username")
    
    if not users:
        print("No users found.")
        print("\nPress Enter to continue...", end="")
        input()
        return
        
    print("Available users:")
    for i, user in enumerate(users, 1):
        print(f"{i}. {user['username']}")
    
    try:
        user_choice = int(input("\nSelect user (number) (or 0 to return): "))
        if user_choice == 0:
            return
            
        if not (1 <= user_choice <= len(users)):
            print("Invalid user selection.")
            return
        
        user_id = users[user_choice-1]['id']
        username = users[user_choice-1]['username']
        
        # Get liked posts
        query = """
        SELECT p.id, p.body, p.timestamp, u.username as author, l.timestamp as liked_at
        FROM like l
        JOIN post p ON l.post_id = p.id
        JOIN user u ON p.user_id = u.id
        WHERE l.user_id = ?
        ORDER BY l.timestamp DESC
        """
        liked_posts = execute_query(conn, query, (user_id,))
        
        clear_screen()
        print(f"\nPosts liked by {username}:")
        
        if liked_posts:
            display_results(liked_posts, "Liked Posts")
        else:
            print("\nThis user hasn't liked any posts yet.")
    except ValueError:
        print("Invalid input.")
    
    print("\nPress Enter to continue...", end="")
    input()

def add_like(conn):
    """Add a like from a user to a post"""
    clear_screen()
    print("\nAdd Like\n========")
    
    # Get users
    users = execute_query(conn, "SELECT id, username FROM user ORDER BY username")
    
    if not users:
        print("No users found.")
        print("\nPress Enter to continue...", end="")
        input()
        return
        
    print("Select user who is liking:")
    for i, user in enumerate(users, 1):
        print(f"{i}. {user['username']}")
    
    try:
        user_choice = int(input("\nSelect user (number): "))
        if not (1 <= user_choice <= len(users)):
            print("Invalid user selection.")
            return
        
        user_id = users[user_choice-1]['id']
        username = users[user_choice-1]['username']
        
        # Get posts that user has not liked yet
        posts_query = """
        SELECT p.id, p.body, u.username as author 
        FROM post p
        JOIN user u ON p.user_id = u.id
        WHERE p.id NOT IN (
            SELECT post_id FROM like WHERE user_id = ?
        )
        ORDER BY p.timestamp DESC
        """
        available_posts = execute_query(conn, posts_query, (user_id,))
        
        if not available_posts:
            print(f"\n{username} has already liked all available posts.")
            print("\nPress Enter to continue...", end="")
            input()
            return
        
        clear_screen()
        print(f"\nSelect post for {username} to like:\n")
        print(tabulate([{
            'ID': post['id'],
            'Author': post['author'],
            'Post': post['body'][:50] + ('...' if len(post['body']) > 50 else '')
        } for post in available_posts], headers="keys", tablefmt="grid"))
        
        post_id = int(input("\nEnter post ID to like (or 0 to return): "))
        if post_id == 0:
            return
        
        # Check if post exists and user hasn't already liked it
        post_exists = False
        for post in available_posts:
            if post['id'] == post_id:
                post_exists = True
                break
                
        if not post_exists:
            print(f"Invalid post ID or {username} has already liked this post.")
            print("\nPress Enter to continue...", end="")
            input()
            return
        
        # Add like
        like_query = """
        INSERT INTO like (user_id, post_id, timestamp)
        VALUES (?, ?, ?)
        """
        timestamp = datetime.utcnow().isoformat()
        result = execute_query(conn, like_query, (user_id, post_id, timestamp))
        
        if result:
            print(f"\nLike added successfully! {username} liked post #{post_id}")
    except ValueError:
        print("Invalid input.")
    except sqlite3.IntegrityError:
        print(f"Error: This user has already liked this post.")
    
    print("\nPress Enter to continue...", end="")
    input()

def remove_like(conn):
    """Remove a like from a post"""
    clear_screen()
    print("\nRemove Like\n===========")
    
    # Get users
    users = execute_query(conn, "SELECT id, username FROM user ORDER BY username")
    
    if not users:
        print("No users found.")
        print("\nPress Enter to continue...", end="")
        input()
        return
        
    print("Select user to remove like from:")
    for i, user in enumerate(users, 1):
        print(f"{i}. {user['username']}")
    
    try:
        user_choice = int(input("\nSelect user (number): "))
        if not (1 <= user_choice <= len(users)):
            print("Invalid user selection.")
            return
        
        user_id = users[user_choice-1]['id']
        username = users[user_choice-1]['username']
        
        # Get posts that user has liked
        liked_query = """
        SELECT p.id, p.body, u.username as author, l.timestamp as liked_at
        FROM like l
        JOIN post p ON l.post_id = p.id
        JOIN user u ON p.user_id = u.id
        WHERE l.user_id = ?
        ORDER BY l.timestamp DESC
        """
        liked_posts = execute_query(conn, liked_query, (user_id,))
        
        if not liked_posts:
            print(f"\n{username} hasn't liked any posts yet.")
            print("\nPress Enter to continue...", end="")
            input()
            return
        
        clear_screen()
        print(f"\nSelect post for {username} to unlike:\n")
        print(tabulate([{
            'ID': post['id'],
            'Author': post['author'],
            'Post': post['body'][:50] + ('...' if len(post['body']) > 50 else ''),
            'Liked on': post['liked_at']
        } for post in liked_posts], headers="keys", tablefmt="grid"))
        
        post_id = int(input("\nEnter post ID to unlike (or 0 to return): "))
        if post_id == 0:
            return
        
        # Check if like exists
        like_exists = False
        for post in liked_posts:
            if post['id'] == post_id:
                like_exists = True
                break
                
        if not like_exists:
            print(f"Invalid post ID or {username} hasn't liked this post.")
            print("\nPress Enter to continue...", end="")
            input()
            return
        
        # Remove like
        unlike_query = """
        DELETE FROM like 
        WHERE user_id = ? AND post_id = ?
        """
        result = execute_query(conn, unlike_query, (user_id, post_id))
        
        if result:
            print(f"\nLike removed successfully! {username} unliked post #{post_id}")
    except ValueError:
        print("Invalid input.")
    
    print("\nPress Enter to continue...", end="")
    input()

def get_like_stats(conn):
    """Show statistics about likes"""
    clear_screen()
    print("\nLike Statistics\n==============")
    
    # Most liked posts
    most_liked_query = """
    SELECT p.id, p.body, u.username as author, COUNT(l.id) as like_count
    FROM post p
    JOIN user u ON p.user_id = u.id
    LEFT JOIN like l ON p.id = l.post_id
    GROUP BY p.id
    ORDER BY like_count DESC
    LIMIT 10
    """
    most_liked = execute_query(conn, most_liked_query)
    
    # Most active likers
    most_active_query = """
    SELECT u.username, COUNT(l.id) as likes_given
    FROM user u
    LEFT JOIN like l ON u.id = l.user_id
    GROUP BY u.id
    ORDER BY likes_given DESC
    LIMIT 10
    """
    most_active = execute_query(conn, most_active_query)
    
    # Most liked users
    most_liked_users_query = """
    SELECT u.username, COUNT(l.id) as received_likes
    FROM user u
    JOIN post p ON u.id = p.user_id
    LEFT JOIN like l ON p.id = l.post_id
    GROUP BY u.id
    ORDER BY received_likes DESC
    LIMIT 10
    """
    most_liked_users = execute_query(conn, most_liked_users_query)
    
    # Recent likes
    recent_likes_query = """
    SELECT u.username as liker, p.id, substr(p.body, 1, 30) as post_preview, 
           a.username as author, l.timestamp
    FROM like l
    JOIN user u ON l.user_id = u.id
    JOIN post p ON l.post_id = p.id
    JOIN user a ON p.user_id = a.id
    ORDER BY l.timestamp DESC
    LIMIT 10
    """
    recent_likes = execute_query(conn, recent_likes_query)
    
    # Display stats
    if most_liked:
        display_results(most_liked, "Most Liked Posts")
    
    if most_active:
        print("\n")
        display_results(most_active, "Most Active Likers")
    
    if most_liked_users:
        print("\n")
        display_results(most_liked_users, "Most Liked Users")
    
    if recent_likes:
        print("\n")
        display_results(recent_likes, "Recent Likes")
    
    print("\nPress Enter to continue...", end="")
    input()

def show_menu():
    """Display the main menu"""
    clear_screen()
    print("""
╔══════════════════════════════════════════╗
║       MICROBLOG DATABASE QUERY TOOL      ║
╚══════════════════════════════════════════╝

1. List all tables and schemas
2. Show all users
3. Show all posts
4. Search users
5. Search posts
6. Add a new post
7. Execute custom SQL query

Likes Management:
8. Show post likes
9. Show user likes
10. Add a like
11. Remove a like
12. Like statistics

0. Exit

Please enter your choice: """, end="")

def main():
    """Main function to run the query tool"""
    # Check if tabulate is installed
    try:
        import tabulate
    except ImportError:
        print("The 'tabulate' package is required. Installing...")
        os.system(f"{sys.executable} -m pip install tabulate")
    
    conn = connect_to_db()
    
    while True:
        show_menu()
        choice = input().strip()
        
        if choice == '0':
            break
        elif choice == '1':
            list_tables(conn)
        elif choice == '2':
            show_all_users(conn)
        elif choice == '3':
            show_all_posts(conn)
        elif choice == '4':
            search_users(conn)
        elif choice == '5':
            search_posts(conn)
        elif choice == '6':
            add_post(conn)
        elif choice == '7':
            custom_query(conn)
        elif choice == '8':
            show_post_likes(conn)
        elif choice == '9':
            show_user_likes(conn)
        elif choice == '10':
            add_like(conn)
        elif choice == '11':
            remove_like(conn)
        elif choice == '12':
            get_like_stats(conn)
        else:
            print("Invalid choice. Press Enter to continue...", end="")
            input()
    
    conn.close()
    print("\nThank you for using the Microblog Database Query Tool!")

if __name__ == "__main__":
    main()