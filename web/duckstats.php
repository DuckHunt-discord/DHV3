<?php
/**
 * Created by IntelliJ IDEA.
 * User: arthur
 * Date: 24/04/2018
 * Time: 01:18
 */

require_once 'vendor/autoload.php';
$servername = "localhost";
$username = "duckhunt_web";
$password = "duckhunt_web";

try {
    $conn = new PDO("mysql:host=$servername;dbname=DHV3", $username, $password);
    // set the PDO error mode to exception
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    //echo "Connected successfully";
} catch (PDOException $e) {
    echo "Connection failed: " . $e->getMessage();
    die;
}


if (isset($_GET['cid']))
{
    $loader = new Twig_Loader_Filesystem('templates');

    $twig = new Twig_Environment($loader, array(
        //'cache' => 'cache',
    ));
    $twig->addExtension(new \Snilius\Twig\SortByFieldExtension());

    $channel_id = (int)$_GET['cid'];
    $db_cid_query = $conn->prepare("SELECT id, channel_name FROM channels WHERE channel=:channel_id");
    $db_cid_query->bindParam(':channel_id', $channel_id);
    $db_cid_query->execute();
    $db_c = $db_cid_query->fetch();
    $db_channel_id = $db_c['id'];
    $db_channel_name = $db_c['channel_name'];

    if (isset($_GET['pid'])) { // On a la channel et le player

        $player_id = (int)$_GET['pid'];
        $player_stats_query = $conn->prepare("SELECT * FROM players WHERE channel_id=:channel_id and id_=:player_id LIMIT 1");
        $player_stats_query->bindParam(':channel_id', $db_channel_id);
        $player_stats_query->bindParam(':player_id', $player_id);
        $player_stats_query->execute();
        $player_stats = $player_stats_query->fetch();

        //print_r($player_stats);



        $player_stats['channel_name'] = $db_channel_name;
        $player_stats['channel_id'] = $channel_id;


        echo $twig->render('duckstats_player.twig', $player_stats);


    } else {
        // Player not passed, displaying chan statistics
        $players_array_query = $conn->prepare("SELECT * FROM players WHERE channel_id=:channel_id AND (exp <> 0 OR killed_ducks > 0) ORDER BY exp DESC");
        $players_array_query->bindParam(':channel_id', $db_channel_id);
        $players_array_query->execute();
        $players_array = $players_array_query->fetchall();

        $total_normal_ducks = 0;
        $total_super_ducks = 0;
        $total_baby_ducks = 0;
        $total_moad_ducks = 0;
        $total_mechanical_ducks = 0;
        $total_players_killed = 0;


        foreach ($players_array as &$player) {
            $total_normal_ducks     += $player['killed_ducks'] - $player['killed_super_ducks'] - $player['killed_baby_ducks'] - $player['killed_mother_of_all_ducks'] - $player['killed_mechanical_ducks'];
            $total_super_ducks      += $player['killed_super_ducks'];
            $total_baby_ducks       += $player['killed_baby_ducks'];
            $total_moad_ducks       += $player['killed_mother_of_all_ducks'];
            $total_mechanical_ducks += $player['killed_mechanical_ducks'];
            $total_players_killed   +=  $player['killed_players'];
        }


        $passed = ["players" => $players_array,
            "channel_name" => $db_channel_name,
            "channel_id" => $channel_id,
            "total_normal_ducks" => $total_normal_ducks,
            "total_super_ducks" => $total_super_ducks,
            "total_baby_ducks" => $total_baby_ducks,
            "total_moad_ducks" => $total_moad_ducks,
            "total_mechanical_ducks" => $total_mechanical_ducks,
            "total_players_killed" => $total_players_killed,
            ];



        echo $twig->render('duckstats_channel.twig', $passed);




    }


} else // Il manque des paramètres, RIP

{

    header("Location: .", true,301);
    die();

}
