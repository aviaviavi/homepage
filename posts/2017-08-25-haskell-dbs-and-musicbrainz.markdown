---
title: Easy database access with Haskell and postgresql-simple
---

## Easy database access with Haskell and postgresql-simple

Working with a database can be a challenging task for newcomers to Haskell. It
was for me, anyway. With libraries like persistent, unfamiliar Template Haskell
combined with the complex types involved ramped the learning curve making it was
hard to get much done.

I found myself needing to write a script to import some data from a data dump
file into postgres (It was a dump of artists from
[musicbrainz](https://musicbrainz.org/) if you're interested). This time, I gave
`postgrseql-simple` a shot and it was surprisingly easy to use! My script ended
up being small and quick to write. If you find yourself just needing a simple
and straightforward way to talk to a database, it's a great choice.

Mapping a data type to a database table and getting a connection is easy:

```haskell
module Main where

import           Control.Monad.IO.Class
import           Data.String.Utils
import           Database.PostgreSQL.Simple
import           Database.PostgreSQL.Simple.FromRow
import           Database.PostgreSQL.Simple.ToRow
import           Database.PostgreSQL.Simple.ToField

-- The data type we want as a table in the database We define our data models as
-- regular data records, no template haskell needed!
data Artist = Artist
  { musicbrainzId :: String
  , name :: String
  }

-- Define a mapping from rows to be unmarshaled into your data type. Just use
-- one literal `<*> field` for each field in your record
instance FromRow Artist where
    fromRow = Artist <$> field <*> field

-- ... And the same for marshaling your datatype into a db row
instance ToRow Artist where
  toRow a = [toField (musicbrainzId a), toField (name a)]
```

We can easily grab a connection like so:

```haskell
main = do
  conn <- connect defaultConnectInfo { connectUser = "my_username"
                                     , connectDatabase = "my_dbname"
                                     }
  -- do some stuff
```

Now we're ready to go! Lets write a function that can insert an artist record.
We can now write:

```haskell
insertArtist :: Connection -> Artist -> IO Int64
insertArtist conn artist =
  execute conn
    "insert into artist (musicbrainz_id, name) values (?, ?)" artist
```

Some things I like about this library:

* Our DB facing methods only need the IO monad, so it's less likely you'll
need to reach for monad transformers to use this productively.
* The database connection is explicitly passed around rather than obfuscated behind a more complicated type.

The trade-off in type safety is well worth the ease of use if, like me, you're
not an expert Haskell developer. Lets tie everything together. To make things a
little more usable, lets also make our insert function print its progress in the
entire import:

```haskell
main = do
  conn <- connect defaultConnectInfo { connectUser = "my_username"
                                     , connectDatabase = "my_dbname"
                                     }
  let artists = ... -- some unrelated file parsing
  mapM_ (uncurry $ insertAndPrintCount conn) $ zip [1 ..] artists
  close conn
  return ()

insertAndPrintCount :: Connection -> Int -> Artist -> IO Int64
insertAndPrintCount  conn count artist = do
  insertedId <- execute conn
    "insert into artist (musicbrainz_id, name) values (?, ?)" artist
  printf "total inserted: %d\n" count
  return insertedId
```
